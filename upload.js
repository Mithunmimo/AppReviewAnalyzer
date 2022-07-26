function submit() {
    let fileElement = document.getElementById('uploader')

    // check if user had selected a file
    if (fileElement.files.length === 0) {
        alert('please choose a file')
        return
    }

    let file = fileElement.files[0]

    let formData = new FormData();
    formData.set('file', file);
};