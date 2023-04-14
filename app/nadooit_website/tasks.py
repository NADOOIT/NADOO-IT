from celery import shared_task
from .models import (
    Session,
    Section_Order,
    Section_Order_Sections_Through_Model,
    Section,
)


@shared_task
def update_session_section_order(session_id, next_section_id):
    session = Session.objects.get(session_id=session_id)
    next_section = Section.objects.get(section_id=next_section_id)

    # Get the current Section_Order of the Session
    current_section_order = session.section_order
    new_section_list = list(current_section_order.sections.all()) + [next_section]

    # Check if there exists an equivalent Section_Order
    equivalent_section_order = None
    for section_order in Section_Order.objects.all():
        sections_with_order = Section_Order_Sections_Through_Model.objects.filter(
            section_order=section_order
        ).order_by("order")
        ordered_sections = [sos.section for sos in sections_with_order]

        if ordered_sections == new_section_list:
            equivalent_section_order = section_order
            break

    # If such an Section_Order exists, replace the Section_Order in the Session
    if equivalent_section_order:
        session.section_order = equivalent_section_order
        session.save()
    else:
        # If no such Section_Order exists, create a new Section_Order with all the Sections from the old Section_Order and add the new Section to the end.
        new_section_order = Section_Order.objects.create()
        for index, section in enumerate(new_section_list):
            Section_Order_Sections_Through_Model.objects.create(
                section_order=new_section_order, section=section, order=index
            )
        new_section_order.save()

        session.section_order = new_section_order
        session.save()
