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



###### Database Stuffs ######


# sql connector
connection = pymysql.connect(host='localhost',user='root',password='Shubham@2507',db='cv')
cursor = connection.cursor()


def insert_data(sec_token, ip_add, host_name, dev_user, os_name_ver, latlong, city, state, country, act_name, act_mail, act_mob, name, email, res_score, timestamp, no_of_pages, reco_field, cand_level, skills, recommended_skills, courses, pdf_name):
    DB_table_name = 'user_data'
    insert_sql = "INSERT INTO " + DB_table_name + " VALUES (0,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    
    # Check if email is provided, insert a placeholder if not
    if not email:
        email = "N/A"  # Placeholder value for missing email
    
    rec_values = (
        str(sec_token), str(ip_add), host_name, dev_user, os_name_ver, str(latlong),
        city, state, country, act_name, act_mail, act_mob, name, email, str(res_score),
        timestamp, str(no_of_pages), reco_field, cand_level, skills, recommended_skills,
        courses, pdf_name
    )
    
    try:
        cursor.execute(insert_sql, rec_values)
        connection.commit()
        print("Data inserted successfully!")
    except pymysql.Error as e:
        connection.rollback()
        print(f"Error inserting data: {e}")



# inserting feedback data into user_feedback table
def insertf_data(feed_name,feed_email,feed_score,comments,Timestamp):
    DBf_table_name = 'user_feedback'
    insertfeed_sql = "insert into " + DBf_table_name + """
    values (0,%s,%s,%s,%s,%s)"""
    rec_values = (feed_name, feed_email, feed_score, comments, Timestamp)
    cursor.execute(insertfeed_sql, rec_values)
    connection.commit()

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


###### Creating Database and Table ######


    # Create the DB
    db_sql = """CREATE DATABASE IF NOT EXISTS CV;"""
    cursor.execute(db_sql)


    # Create table user_data and user_feedback
    DB_table_name = 'user_data'
    table_sql = "CREATE TABLE IF NOT EXISTS " + DB_table_name + """
                    (ID INT NOT NULL AUTO_INCREMENT,
                    sec_token varchar(20) NOT NULL,
                    ip_add varchar(50) NULL,
                    host_name varchar(50) NULL,
                    dev_user varchar(50) NULL,
                    os_name_ver varchar(50) NULL,
                    latlong varchar(50) NULL,
                    city varchar(50) NULL,
                    state varchar(50) NULL,
                    country varchar(50) NULL,
                    act_name varchar(50) NOT NULL,
                    act_mail varchar(50) NOT NULL,
                    act_mob varchar(20) NOT NULL,
                    Name varchar(500) NOT NULL,
                    Email_ID VARCHAR(500) NOT NULL,
                    resume_score VARCHAR(8) NOT NULL,
                    Timestamp VARCHAR(50) NOT NULL,
                    Page_no VARCHAR(5) NOT NULL,
                    Predicted_Field BLOB NOT NULL,
                    User_level BLOB NOT NULL,
                    Actual_skills BLOB NOT NULL,
                    Recommended_skills BLOB NOT NULL,
                    Recommended_courses BLOB NOT NULL,
                    pdf_name varchar(50) NOT NULL,
                    PRIMARY KEY (ID)
                    );
                """
    cursor.execute(table_sql)


    DBf_table_name = 'user_feedback'
    tablef_sql = "CREATE TABLE IF NOT EXISTS " + DBf_table_name + """
                    (ID INT NOT NULL AUTO_INCREMENT,
                        feed_name varchar(50) NOT NULL,
                        feed_email VARCHAR(50) NOT NULL,
                        feed_score VARCHAR(5) NOT NULL,
                        comments VARCHAR(100) NULL,
                        Timestamp VARCHAR(50) NOT NULL,
                        PRIMARY KEY (ID)
                    );
                """
    cursor.execute(tablef_sql)

   
run()

