var nowx = 1, nowy = 2, maxX = 1, maxY = 2, nextX = 1, nextY = 2;
var keyBoardMode = true;
console.log(csrftoken)
var direction = 0;
var directionStr = "→↓↑←";
document.addEventListener('keydown', (event) => {
  const keyName = event.key;
  // console.log(`Key pressed "${keyName}"`);

  if ("ArrowDownArrowUpArrowRightArrowLeftEnter".includes(keyName)) {
    switch (keyName) {
    case 'ArrowDown':
      selection(1, 0);
      break;
    case 'ArrowUp':
      selection(-1, 0);
      break;
    case 'ArrowRight':
      selection(0, 1);
      break;
    case 'ArrowLeft':
      selection(0, -1);
      break;
    }
    // console.log(`Key pressed ${keyName}`);
  }
  if (keyName == "Backspace" || keyName == " ") {
    document.getElementById('tble').rows.item(nowx).cells.item(nowy).innerHTML =
        "";
  }
  if ("1234567890yн".includes(keyName)) {
    if (nowx != 0) {
      var kleyName = keyName;
      if (kleyName == "y") {
        kleyName = "н";
      }
      if (kleyName == "0") {
        kleyName = "10";
      }

      document.getElementById('tble')
          .rows.item(nowx)
          .cells.item(nowy)
          .innerHTML = kleyName;
    }
  }
  // console.log(`Key pressed ${keyName}`);
}, false);
function directionChange() {
  if (direction == 3) {
    direction = 0
  } else {
    direction += 1;
  }
  document.getElementById('kf1').innerHTML = `dc ${directionStr[direction]}`;
  console.log(directionStr[direction]);
}
function keyBoardModeChange() {
  console.log();
  document.getElementById('k1').innerHTML = keyBoardMode ? "" : "1";
  document.getElementById('k2').innerHTML = keyBoardMode ? "↑" : "2";
  document.getElementById('k3').innerHTML = keyBoardMode ? "" : "3";
  document.getElementById('k4').innerHTML = keyBoardMode ? "←" : "4";
  document.getElementById('k5').innerHTML = keyBoardMode ? "" : "5";
  document.getElementById('k6').innerHTML = keyBoardMode ? "→" : "6";
  document.getElementById('k7').innerHTML = keyBoardMode ? "" : "7";
  document.getElementById('k8').innerHTML = keyBoardMode ? "↓" : "8";
  document.getElementById('k9').innerHTML = keyBoardMode ? "" : "9";
  document.getElementById('k10').innerHTML = keyBoardMode ? "" : "10";

  if (keyBoardMode) {
    keyBoardMode = false;
  } else {
    keyBoardMode = true;
  }
}
function keybev(ev) {
  if (!(typeof ev === "string")) {
    keyName = ev.srcElement.innerHTML;
  } else {
    keyName = ev;
  }
  console.log(keyName);
  switch (keyName) {
  case "↓":
    selection(1, 0);
    break;
  case "↑":
    selection(-1, 0);
    break;
  case "→":
    selection(0, 1);
    break;
  case "←":
    selection(0, -1);
    break;
  default:
    document.getElementById('tble').rows.item(nowx).cells.item(nowy).innerHTML =
        keyName;
    keybev(directionStr[direction]);
  }
}
function selection(x, y) {
  var nextX = (nowx + x);
  var nextY = (nowy + y);

  if ((nextX >= 0 && nextX < maxX) && (nextY > 1 && nextY < maxY)) {

    updateSelection(nextX, nextY);
    console.log(`Selection x=${nowx},y=${nowy}`);
  }
}
function getTableSize() {
  var myTab = document.getElementById('tble');
  if (myTab) {
    maxX = myTab.rows.length;
    maxY = myTab.rows.item(0).cells.length;
    console.log(`size x=${maxX},y=${maxY}`);
  }
}
function updateSelection(nextX = nowx, nextY = nowy) {
  var myTab = document.getElementById('tble');
  var elements = document.getElementsByClassName("active");
  var sel = myTab.rows.item(nextX).cells.item(nextY);
  for (var i = 0; i < elements.length; i++) {
    elements[i].setAttribute("class", "");
  }
  sel.setAttribute("class", "active");

  nowx = nextX;
  nowy = nextY;
}

function uploadTableToServer(event) {
  var array = [];
  var myTab = document.getElementById('tble');
  for (var i = 0; i < myTab.rows.length; i++) {
    var objCells = myTab.rows.item(i).cells;
    var tmpArr = [];
    for (var j = 2; j < objCells.length; j++) {
      if (i == 0) {
        tmpArr.push(objCells.item(j).children[0].children[0].value)
      } else {
        tmpArr.push(objCells.item(j).innerHTML);
      }
    }
    array.push(tmpArr);
  }
  console.log(array)
  console.log(document.location.href)

  $.ajax({
    type : "POST",
    url : "/resiveTable",
    data : {"table" : JSON.stringify(array), "params" : document.location.href},
    headers : {'X-CSRFToken' : csrftoken},
    success :
        function() { $('#message').html("<h2>Contact Form Submitted!</h2>") },
    error : function() { $('#message').html("<h2>Contact Form error!</h2>") }

  });
  return false;
}
$(document).ready(function() { $("#test").submit(uploadTableToServer); });

$(window).resize(function() {

});

window.onload = function() {
  getTableSize();
  updateSelection();
  // $("#0").height($(".dates").width());
  // $('#sizeInfo').text('size: ' + width + ' x ' + height);
  // makeDraggable();
  // init();
  $('.rotate').css('width', $('.rotate').height());
};
