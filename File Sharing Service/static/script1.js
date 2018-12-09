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

function signInClicked(){
    var email = document.getElementById('emailField').value;
    var pass = document.getElementById('passField').value;
    var found = false;
    var passed = false;
    loadJSON("/static/loginInfo.json", function(response) {
        var actual_JSON = JSON.parse(response);
        actual_JSON.users.forEach(user => {
            if(user.login == email && user.password == pass){
                window.location.href = 'box/';
                found = true;
                passed = true;
                return;
            } 
            if(user.login == email){
                found = true;
            }
        });  
        if(found && !passed){
            window.alert("Wrong login or password");
        } else if(!found) {
            window.alert("User with that email not yet registered!")
        }
    });
}

function signUpClicked(){
    var email = document.getElementById('emailField').value;
    var name = document.getElementById('nameField').value;
    var pass = document.getElementById('passField').value;
    var found = false;
    loadJSON("/static/loginInfo.json", function(response) {
        var actual_JSON = JSON.parse(response);
        actual_JSON.users.forEach(user => {
            if(user.login == email){
                found = true;
            }
        });  
        if(found){
            window.alert("User with that email already registered");
        }else {
            actual_JSON.users.push({name: name, login: email, password: pass});
        }
    });
}

function uploadFiles(){
    var fileToUpload = document.getElementById('fileUpload').value.replace('C:\\fakepath\\','');
    var label = document.getElementById('fileLabel');
    label.innerHTML = "File to upload: " + fileToUpload;
    label.style.display = 'inline-block';
}

function loadJSON(file, callback) {   

    var xobj = new XMLHttpRequest();
    xobj.overrideMimeType("application/json");
    xobj.open('GET', file, true); // Replace 'my_data' with the path to your file
    xobj.onreadystatechange = function () {
          if (xobj.readyState == 4 && xobj.status == "200") {
            // Required use of an anonymous callback as .open will NOT return a value but simply returns undefined in asynchronous mode
            callback(xobj.responseText);
          }
    };
    xobj.send(null);  
 }

 