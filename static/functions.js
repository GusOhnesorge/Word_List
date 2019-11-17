
function select_set(){
  var new_option;
  var select = document.querySelector("#select_length");
  for(let i = 3; i<11; i++){
    new_option = document.createElement("OPTION");
    new_option.text = i;
    new_option.value = i;
    select.appendChild(new_option);
  }
}

async function open_def(word_obj) {
  var def_box = document.querySelector("#definition_box");
  var def_title = document.querySelector("#definition_title");
  var def_text = document.querySelector("#definition_text");
  word = word_obj.innerText;
  def_title.innerText = word;
  let infoopts = {
    method: 'GET'
  };
  let def_promise = await fetch(`/def/${word}`);
  let def_string = await def_promise.text();
  def_text.innerText = def_string;
  def_box.style.display = "block";
}


function close_def() {
  var def_box = document.querySelector("#definition_box");
  def_box.style.display = "none";
}
