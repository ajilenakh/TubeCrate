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
            const listContainer = document.getElementById('responseList');

            // Clean the previous content in the list
            listContainer.innerHTML = '';

            // Looping through each item and create the list
            items.forEach(item => {
                if (item.format_note && item.highest_filesize) {
                    const notes = item.format_note;
                    const filesize = (item.highest_filesize / 1000000).toFixed(2);

                    if (/\p/.test(item.format_note)) {
                        const listItem = document.createElement('li');
                        listItem.textContent = `${notes} | ${filesize} MB`;

                        listItem.addEventListener('click', () => {
                            postVideoRequest(InputUrl,item.format_id);
                        });
                    
                        listContainer.appendChild(listItem);
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            const listContainer = document.getElementById('responseList');
            listContainer.innerHTML = `Error: ${error.message}`;
        });
    };

async function postVideoRequest(url,format_id){
    const data =
    {
        url: `${url}`,
        video_format_id: `${format_id}` 
    };
    
    fetch((`${api_address}/process_video/`),{
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const responseData = response.text();
        console.log(responseData);
        return response;
    })
}