20.04.2023

- Update Server Version of Website
- Create new Section_Order for the default.
    def get_most_successful_section_order():
        # Replace this with the actual logic for finding the most successful Section_Order
        return Section_Order.objects.get(
            section_order_id="7b3064b3-8b6c-4e3e-acca-f7750e45129b"
        )
    
    Hier muss die neue id hinterlegt werden.
    
- Test if everything works
- Change the Old Index Website into the new one (just comment out the old one)
- Change the new Index into the new one
- 