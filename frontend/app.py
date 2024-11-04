import streamlit as st
import requests

# Set the title of the app
st.title("JLABGPT Streamlit UI")

# Input text box for the user
user_input = st.text_input("Enter your query:", "")

# Button to submit the query
if st.button("Submit"):
    if user_input:
        # Define the endpoint URL
        api_url = f"http://0.0.0.0:8000/api/v1/rag/stream?query={user_input}"

        # Create the JSON payload
        payload = {"query": user_input}
        headers = {
            'accept': 'application/json'
        }

        # Send GET request to the FastAPI backend
        try:
            response = requests.post(api_url, headers=headers)

            # Check if the request was successful
            if response.status_code == 200:
                st.write("Response:")
                # Stream and display the response line by line
                for line in response.iter_lines():
                    if line:
                        st.write(line.decode("utf-8"))
            else:
                st.error("Failed to get response from the backend.")
        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to the backend: {e}")
    else:
        st.warning("Please enter a query.")
