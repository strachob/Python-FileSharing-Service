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
    label.innerHTML = "File to upload: " + fileToUpload;
    label.style.display = 'inline-block';
}

user = document.currentScript.getAttribute('user');

var cos = new EventSource('https://pi.iem.pw.edu.pl:6889/strachob/events/sub/'+ user);

cos.onmessage = function(e){
     alert(e.data);
};
 
