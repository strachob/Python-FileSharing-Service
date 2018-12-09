function field_focus(field, email) {
    if (field.value == email) {
      field.value = ''; 
    }
}

function field_blur(field, email) {
    if (field.value == '') {
      field.value = email; 
    }
}


function uploadFiles(){
    var fileToUpload = document.getElementById('fileUpload').value.replace('C:\\fakepath\\','');
    var label = document.getElementById('fileLabel');
    var labelError = document.getElementById('fileLabel2');
    label.innerHTML = "File to upload: " + fileToUpload;
    label.style.display = 'inline-block';
    labelError.style.display = 'none';
}

 
