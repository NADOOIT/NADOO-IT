from celery import shared_task
from .models import (
    Session,
    Section_Order,
    Section_Order_Sections_Through_Model,
    Section,
)
from django.db.models import Count


@shared_task
def update_session_section_order(session_id, next_section_id):
    session = Session.objects.get(session_id=session_id)
    next_section = Section.objects.get(section_id=next_section_id)

    # Get the current Section_Order of the Session
    current_section_order = session.session_section_order

    # Fetch the Section_Order_Sections_Through_Model objects for the current section order
    current_section_order_sections = (
        current_section_order.sections.through.objects.filter(
            section_order=current_section_order
        ).order_by("order")
    )
    current_section_order_sections_ids = [
        section.section_id for section in current_section_order_sections
    ]

    # Build the new section list by appending the next section
    new_section_list = current_section_order_sections_ids + [next_section_id]

    # Check if there exists an equivalent Section_Order
    equivalent_section_order = None
    for section_order in Section_Order.objects.annotate(count=Count("sections")).filter(
        count=len(new_section_list)
    ):
        sections_with_order = Section_Order_Sections_Through_Model.objects.filter(
            section_order=section_order
        ).order_by("order")
        ordered_sections = [sos.section_id for sos in sections_with_order]

        if ordered_sections == new_section_list:
            equivalent_section_order = section_order
            break

    # If such an Section_Order exists, replace the Section_Order in the Session
    if equivalent_section_order:
        session.session_section_order = equivalent_section_order
        session.save()
    else:
        # If no such Section_Order exists, create a new Section_Order with all the Sections from the old Section_Order and add the new Section to the end.
        new_section_order = Section_Order.objects.create()
        for index, section_id in enumerate(new_section_list):
            Section_Order_Sections_Through_Model.objects.create(
                section_order=new_section_order, section_id=section_id, order=index
            )
        new_section_order.save()

        session.session_section_order = new_section_order
        session.save()
