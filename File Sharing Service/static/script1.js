function uploadFiles(){
    var fileToUpload = document.getElementById('inputGroupFile01').value.replace('C:\\fakepath\\','');
    var label = document.getElementById('fileLabel');
    label.innerHTML = "File to upload: " + fileToUpload;
    label.style.display = 'inline-block';
}

user = document.currentScript.getAttribute('user');

var cos = new EventSource('https://127.0.0.1:6889/strachob/events/sub/'+ user);

cos.onmessage = function(e){
     alert(e.data);
};
 
$('#inputGroupFile01').on('change',function(){
    //get the file name
    var fileName = $(this).val();
    var fileToUpload = fileName.replace('C:\\fakepath\\','');
    //replace the "Choose a file" label
    $(this).next('.custom-file-label').html(fileToUpload);
})
