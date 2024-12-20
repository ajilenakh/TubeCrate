const api_address = "https://0.0.0.0:8000";

    async function getResolutions() {
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
            if (!Array.isArray(data)){
                throw new Error('Expected an array of items in the response');
            }

            const items = data;
            const refrnceElement = document.getElementById('toDynamicallyLoadSelectElement')
            const container = document.querySelector('.content')

            const selectElement = document.createElement('select');
            selectElement.id = 'videoSelect';

            // Insert the select element before the refrenceElement
            container.insertBefore(selectElement, refrnceElement)

            // Looping through each item and create the list
            items.forEach(item => {
                if (item.format_note && item.highest_filesize) {
                    const notes = item.format_note;
                    const filesize = (item.highest_filesize / 1000000).toFixed(2);  // Convert to MB
            
                    // Check if the format_note matches your regex
                    if (/\p/.test(item.format_note)) {
                        const option = document.createElement('option');
                        option.value = item.format_id; 
                        option.textContent = `${notes} | ${filesize} MB`;
            
                        // Add the option to the select element
                        selectElement.appendChild(option);
                    }
                }
            });
            // change the button to get link
            const button = document.getElementById('check');
            button.textContent = 'Get Link';
            button.id = 'getLinkButton';
            button.removeAttribute('onclick');

            button.addEventListener('click', function(){
                (selectElement.value)
                postVideoRequest(InputUrl, selectElement.value);
                
            });
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            const selectElement = document.getElementById('responseList');
            selectElement.innerHTML = `Error: ${error.message}`;
        });
    };

async function postVideoRequest(url, format_id) {
    const data = {
        url: `${url}`,
        video_format_id: `${format_id}`,
    };

    try {
        const response = await fetch(`${api_address}/process_video/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const responseData = await response.json();
        console.log('Video processed:', responseData);

        await downloadLink(responseData.unique_id, responseData.file_name);

    } catch (error) {
        // Log any errors and return them as JSON
        console.error("Error during fetch or data processing:", error);
        return { error: error.message };  // Return error as JSON
    }
}

async function downloadLink(unique_id, file_name) {
    try {
        const downloadResponse = await fetch(`${api_address}/videos/${unique_id}/${file_name}`);

        if (!downloadResponse.ok) {
            throw new Error('Failed to download the video');
        }

        const blob = await downloadResponse.blob(); // Get the file as a Blob
        const link = document.createElement('a');    // Create a temporary <a> element
        link.href = URL.createObjectURL(blob);       // Create an object URL for the Blob
        link.download = file_name;                   // Set the filename for download
        link.click();                                // Trigger the download by simulating a click

        console.log("Download started for file:", file_name);

    } catch (error) {
        console.error("Error during download:", error);
    }
}