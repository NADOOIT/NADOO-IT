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

22.04.2023 - 30.04.2023

Topic: NADOOIT Website Videohosting

Because we do not want to have a cookie banner we need to host the videos on our own server. We need to find a way to do this.
Videos can be part of website sections.

- [ ] Find a way to host videos on our own server
- [ ] Use https://github.com/videojs/video.js/ as a player

- [ ] Create a preview image for the video
- [ ] Create a way to upload and view videos in the admin panel
- [ ] Add a way to integrate a video in the template of the section without having the id of the video in the template. Instead do something likse this:
    {% video section.video %}
    This way we can change the video in the admin panel and it will be changed in the template as well.
    To do this we need to create a custom template tag, filter or context processor.
- [ ] Create a way to have playlists of videos
- [ ] Create a new section with a video
- [ ] Create a new section with a playlist of videos
