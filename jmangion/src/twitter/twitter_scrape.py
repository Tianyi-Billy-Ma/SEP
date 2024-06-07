from twikit import Client

def login_credentials():
    print("attempting login with credentials")
    client = Client('en-US')
    with open("login.txt", "r") as f:
        USERNAME, EMAIL, PASSWORD = f.read().splitlines()
        print("stored login information")
    client.login(
        auth_info_1=USERNAME ,
        auth_info_2=EMAIL,
        password=PASSWORD
    )
    print("storing cookies in cookies.json")
    client.save_cookies('cookies.json')
    return client

def login_cookies():
    print("attempting login in with cookies")
    client = Client('en-US')
    client.load_cookies('cookies.json')
    return client

def main():
    #client = login_credentials()
    client = login_cookies()
    print("logged in!")
    query = "weed"
    result = client.search_user(query, count = 1)
    print(type(result))
    for user_id in list(result):
        print(user_id) 











if __name__ == '__main__':
    main()
