function registerE(errorArray){
    let username = document.getElementById('username');
    let password = document.getElementById('password');
    let confirmPassword = document.getElementById('confirmPassword');

    if (errorArray.includes(0)){
      username.classList.add('is-invalid');
      document.getElementById('username_error').innerHTML = 'Please choose a username.';
    }
    else if (errorArray.includes(4)) {
      username.classList.add('is-invalid');
      document.getElementById('username_error').innerHTML = 'Username already taken.';
    }
    else {
      username.classList.add('is-valid');
    }

    if (errorArray.includes(1)) {
      password.classList.add('is-invalid')
      document.getElementById('password_error').innerHTML = 'Please enter a password.'
    }
    else {
      password.classList.add('is-valid')
    }

    if (errorArray.includes(2)) {
      confirmPassword.classList.add('is-invalid')
      document.getElementById('confirmPassword_error').innerHTML = 'Please confirm your password.'
    }
    else if (errorArray.includes(3)) {
      confirmPassword.classList.add('is-invalid')
      document.getElementById('confirmPassword_error').innerHTML = 'Passwords do not match.'
    }
    else {
      confirmPassword.classList.add('is-valid')
    }
}

function loginE(errorArray){
    let username = document.getElementById('username');
    let password = document.getElementById('password');

    if (errorArray.includes(0)){
      username.classList.add('is-invalid');
      document.getElementById('username_error').innerHTML = 'Please enter your username.';
    }
    else if (errorArray.includes(5)) {
      username.classList.add('is-invalid');
      document.getElementById('username_error').innerHTML = 'Invalid username.';
    }
    else {
      username.classList.add('is-valid');
    }

    if (errorArray.includes(1)) {
      password.classList.add('is-invalid')
      document.getElementById('password_error').innerHTML = 'Please enter your password.'
    }
    else if (errorArray.includes(6)){
      password.classList.add('is-invalid')
      document.getElementById('password_error').innerHTML = 'Invalid password.'
    }
}

function updateFields() {     
  var selectedValue = document.getElementById('inputType').value;
  document.getElementById('inputType').classList.add(selectedValue === '' ? 'b': 'is-valid');
  document.getElementById('selectVal').value = selectedValue;

  document.getElementById('nameField').style.display = selectedValue === 'name' ? 'block' : 'none';
  document.querySelector('#nameField input').required = selectedValue === 'name';
  document.getElementById('steamAppidField').style.display = selectedValue === 'steam_appid' ? 'block' : 'none';
  document.querySelector('#steamAppidField input').required = selectedValue === 'steam_appid';
  document.getElementById('vndbidField').style.display = selectedValue === 'vndbid' ? 'block' : 'none';
  document.querySelector('#vndbidField input').required = selectedValue === 'vndbid';
  document.getElementById('addGameFormDiv').style.display = selectedValue === '' ? 'none' : 'block';

}
