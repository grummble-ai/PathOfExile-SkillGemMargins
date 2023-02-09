import streamlit as st
import widgets.initializer as initializer
from utility.plot_utility import get_img_with_href as get_img_with_href

# add_action_to_db(st.session_state.db_connection,
#                  viewer_id=st.session_state.viewer_id,
#                  document=u"actions_toolbox")

TITLE = "Build Guide Buttler"
SUBHEADER = '''
            Hey, exile! This is an idea I have in mind for a long time: Creating a single place that gathers all the 
             build guides currently available to us.
            '''
initializer.create_boilerplate(pagetitle=TITLE, version="", subheader=SUBHEADER)

st.markdown('''Not gonna lie, this idea is heavily inspired by poebuild.cc. It's a great website but a little bit 
            outdated IMO as it only features guides from the PoE forums.''')

# image = Image.open("img/poebuilds_screenshot.png")
# st.image(image, width=300)

st.write('''
        Here's a rough **sketch** of what I'd try to include in a new tool:\n
        - **Multiple Build Sources**: YT, PoE Forums, Websites, Reddit, tc.
        - **Filter Options**: Classes, Ascendancies, Skills, etc.
        - **Add some Analytics**: Show view count, comments, upvote/downvote-ratio
        - **Sanity checks**: unique items in the build cost at least X divines, guide was updated on date Y the last time,?  
        - **Collaboration Opportunity**: You have killed Uber Elder with the build or just wants to show its playstyle? Simply attach a video-of-proof and the corresponding pob to the guide you follow!
        ''')

st.markdown('''Especially the last point is something I'd love to see turn into reality. You want this, too? Read below
            how you can make it happen.''')

st.markdown("-----")

st.markdown('''**Problem:** This would take a lot of effort to create. So much effort that I'm not willing to put 
            that much effort into before knowing that the community really wants it''')

st.markdown('''**Solution:** If you think that creating something like this would help you a lot, become a Patron of
            mine and make this tool happen when we reach 100€/Month (**click the image below**):''')
# taken from: https://discuss.streamlit.io/t/href-on-image/9693/4
png_html = get_img_with_href('img/Digital-Patreon-Wordmark_FieryCoral.png',
                             'https://www.patreon.com/user/membership?u=86747551',
                             10)
st.markdown(png_html, unsafe_allow_html=True)