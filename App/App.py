#Packages
import streamlit as st 
from PIL import Image
import time
import datetime

#Page Configuration
st.set_page_config(
   page_title="Resume Insight",
   page_icon='./Logo/recommend.png',
)

#Main function
def run():
    
    #Logo and Heading
    img = Image.open('./Logo/RESUM.png')
    st.image(img)
    st.title("Resume Insight")

    #Dropdown menu
    selection = st.selectbox(" ", ("", "User", "Admin"))
    
    #Buttons for User and Admin
    if selection == "User":
        #Collecting Information
        act_name = st.text_input('Name*')
        act_mail = st.text_input('Mail*')
        act_mob  = st.text_input('Mobile Number*')
        
        #Upload Resume
        st.markdown('''<h5 style='text-align: left; color: #021659;'> Upload Your Resume </h5>''',unsafe_allow_html=True)
  
        #Feedback
        if st.button('Feedback'):   
            #timestamp 
            ts = time.time()
            cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
            cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
            timestamp = str(cur_date+'_'+cur_time)

            #Feedback Form
            with st.form("my_form"):
                st.write("Feedback form")            
                feed_name = st.text_input('Name')
                feed_email = st.text_input('Email')
                feed_score = st.slider('Rate Us From 1 - 5', 1, 5)
                comments = st.text_input('Comments')
                Timestamp = timestamp        
                submitted = st.form_submit_button("Submit")
                if submitted:
                    st.success("Thanks! Your Feedback was recorded.") 
        
    if selection == "Admin":
        #Admin Login
        ad_user = st.text_input("Username")
        ad_password = st.text_input("Password", type='password')

        if st.button('Login'):
            #Credentials 
            if ad_user == 'admin' and ad_password == 'admin@resume-analyzer':
                st.success('Welcome to Admin Side')  
            #Wrong Credentials
            else:
                st.error("Wrong ID & Password Provided")
        st.write(" ")
    
    #About
    if st.button("About"):
        st.subheader("**About The Tool - AI RESUME ANALYZER**")
        st.markdown('''

        <p align='justify'>
            A tool which parses information from a resume using natural language processing and finds the keywords, cluster them onto sectors based on their keywords. And lastly show recommendations, predictions, analytics to the applicant based on keyword matching.
        </p>

        ''',unsafe_allow_html=True)  
   
run()

