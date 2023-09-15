# importing important libraries and packages
from selenium import webdriver
from selenium.webdriver.common.by import By

import psycopg2
import urllib.parse as up

import time
import uuid
from datetime import datetime

# getting user input for linkedin email and pwd
email = input("Enter LinkedIn email : ")
pwd = input("Enter LinkedIn password ; ")


def scrape():

    # initialising the driver
    driver = webdriver.Chrome()

    # loading linkedin website
    driver.get("https://www.linkedin.com/")

    # waiting for 2 seconds to fully load the website
    time.sleep(5)

    # finding the input fields and inputiing the credentials
    driver.find_element(By.ID, "session_key").send_keys(email)
    driver.find_element(By.ID, "session_password").send_keys(pwd)
    driver.find_element(By.XPATH, "/html/body/main/section[1]/div/div/form/div[2]/button").click()

    time.sleep(2)

    driver.get("https://www.linkedin.com/company/chelsea-football-club/")

    time.sleep(5)

    profile_name = driver.find_element(By.TAG_NAME, "h1").text
    followers = int("".join(driver.find_elements(By.CLASS_NAME, "org-top-card-summary-info-list__info-item")[2].text.split("followers")[0].split(",")))
    profile_img_url = driver.find_element(By.ID, "ember29").get_attribute("src")
    about = driver.find_element(By.CLASS_NAME, "organization-about-module__content-consistant-cards-description").text
    url = driver.current_url

    linkedin_account_info = {
        "account_id": str(uuid.uuid4()),
        "platform": "LinkedIn",
        "account": url.split("/")[-1],
        "account_url": url,
        "name": profile_name,
        "followers": followers,
        "profile_image_url": profile_img_url,
        "bio": about,
        "created_date_utc": datetime.utcnow(),
        "updated_date_utc": None,  # Set to None as it's initially empty
    }

    save(linkedin_account_info)


def save(linkedin_account_info):

    insert_query = """
        INSERT INTO linkedin_account_info 
        (account_id, platform, account, account_url, name, followers, profile_image_url, bio, updated_date_utc)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
    """

    update_query = """
        UPDATE linkedin_account_info 
        SET name = %s, followers = %s, profile_image_url = %s, bio = %s, updated_date_utc = NOW()
        WHERE account = %s;
    """

    try:
      
        with connection.cursor() as cursor:
            cursor.execute(insert_query, (
                linkedin_account_info["account_id"],
                linkedin_account_info["platform"],
                linkedin_account_info["account"],
                linkedin_account_info["account_url"],
                linkedin_account_info["name"],
                linkedin_account_info["followers"],
                linkedin_account_info["profile_image_url"],
                linkedin_account_info["bio"],
                linkedin_account_info["updated_date_utc"]
            ))
    
    except:

         with connection.cursor() as cursor:
            cursor.execute(update_query, (
                linkedin_account_info["name"],
                linkedin_account_info["followers"],
                linkedin_account_info["profile_image_url"],
                linkedin_account_info["bio"],
                linkedin_account_info["account"]           
            ))

    connection.commit()
    connection.close()



if __name__ == "__main__":

    up.uses_netloc.append("postgres")
    DATABASE_URL = "DATABASE URI"
    url = up.urlparse(DATABASE_URL)
    connection = psycopg2.connect(database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )

    create_table_query = """
            CREATE TABLE IF NOT EXISTS linkedin_account_info (
                id SERIAL PRIMARY KEY,
                account_id UUID DEFAULT uuid_generate_v4() NOT NULL,
                platform TEXT,
                account TEXT UNIQUE,
                account_url TEXT,
                name TEXT,
                followers INT,
                profile_image_url TEXT,
                bio TEXT,
                created_date_utc TIMESTAMP DEFAULT NOW(),
                updated_date_utc TIMESTAMP
            );
        """


    with connection.cursor() as cursor:
        cursor.execute(create_table_query)
        connection.commit()
        cursor.close()      
    
    scrape()