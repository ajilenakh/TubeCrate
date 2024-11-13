
const api_address = "https://0.0.0.0:8000";

    function getResolutions() {
        // Get the value from the input field
        var InputUrl = document.getElementById("url").value;

        if (!InputUrl) {
            alert("Please enter a valid URL!");
            return;
        }

        // Send the GET request to the API endpoint
        fetch(`${api_address}/filter_resolution/?url=${InputUrl}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log(data);  // Process the API response data
            })
            .catch(error => {
                console.error('There was a problem with the fetch operation:', error);
                alert("There was an error fetching the resolutions.");
            });
    }