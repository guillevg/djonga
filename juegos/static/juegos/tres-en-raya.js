"use strict";

class TicTacToeBoard {
  constructor() {
    this.canvas = document.getElementById("canvasBoard");
    console.log(this.canvas.width);
    this.x = 0;
    this.y = 0;
    this.d = 20;
    this.l = (this.canvas.width - 2 * this.d)/3 - 1;
    this.colors = ["#000", "#f00", "#00f"];
    this.moves = [[0, 0, 0], [0, 0, 0], [0, 0, 0]];
  }
  drawCell(i, j) {
    //console.log('drawing: ', i, j);
    //var canvas = document.getElementById("canvasBoard");
    var context = this.canvas.getContext('2d');
    //console.log(this);
    let x = this.x + i * (this.l + this.d);
    let y = this.y + j * (this.l + this.d);
    context.beginPath();
    context.rect(x, y, this.l, this.l);
    context.closePath();
    context.lineWidth = 0;
    context.lineJoin = 'miter';
    context.strokeStyle = '#000';
    //context.lineJoin = 'round';
    context.stroke();
    // Fill our new polygon
    context.fillStyle = this.colors[this.moves[i][j]];
    context.fill();
  }
  drawBoard() {
    for (let i = 0; i < 3; i++) {
      for (let j = 0; j < 3; j++) {
        this.drawCell(i, j);
      }
    }
  }
}

class TicTacToeGame {
  constructor() {
    this.board = new TicTacToeBoard();
    this.juega = 1;
    this.turno = 0;
  }
  move(i, j) {
    if (this.board.moves[i][j] == 0) {
      this.board.moves[i][j] = this.juega;
      this.turno += 1;
      console.log(this.board.moves);
      console.log('ahora es el turno del jugador', this.juega);
      console.log('turno', this.turno)
      this.juega = 3 - this.juega;
      this.board.drawCell(i, j);
    }
  }
}

function mouseClicked(event) {
  console.log('click!');
  console.log(game);
  var mouseX = event.pageX;
  var mouseY = event.pageY;
  var i = parseInt((mouseX - game.board.x) / (game.board.l + game.board.d));
  var j = parseInt((mouseY - game.board.y) / (game.board.l + game.board.d));
  game.move(i, j);
  const turno = game.turno;
  const fila = i;
  const columna = j;
  const juega = game.juega;
  console.log(fila, columna, turno, juega);
  chatSocket.send(JSON.stringify({
    'juega': juega,
    'fila': fila,
    'columna': columna,
    'turno': turno,
  }));
  /*
    let turn = 1 + (game.turn % 2);
    game.board.board[ii][jj].setState(turn);
    game.board.touchCell(ii, jj, 1);
    game.board.turn += 1;
    */
}

const gameSlug = JSON.parse(document.getElementById('slug').textContent);
const idPartida = JSON.parse(document.getElementById('id_partida').textContent);
const chatSocket = new WebSocket(
'ws://'
  + window.location.host
  + '/ws/juegos/'
  + gameSlug
  + '/'
  + idPartida
  + '/'
);
chatSocket.onmessage = function(e) {
  const data = JSON.parse(e.data);
  document.querySelector('#chat-log').value += (data.juega + ' juega en ' + data.fila + ', ' + data.columna + '\n');
  if (data.juega) {
    game.move(data.fila, data.columna);
  }
};
chatSocket.onclose = function(e) {console.error('Chat socket closed unexpectedly');
};
/*
document.querySelector('#chat-message-input').focus();
document.querySelector('#chat-message-input').onkeyup = function(e) {
  if (e.keyCode === 13) { // enter, return
    document.querySelector('#chat-message-submit').click();
  }
};
document.querySelector('#chat-message-submit').onclick = function(e) {
  const messageInputDom = document.querySelector('#chat-message-input');
  const message = messageInputDom.value;
  chatSocket.send(JSON.stringify({
'message': message
  }));
  messageInputDom.value = '';
};
*/

//let board = new HexHexBoard(CatchupCell, 5, 40, BOARD_CANVAS, 1);
//let boardH = new HexHexBoard(CatchupCell, 5, 40, HIDDEN_CANVAS, 0);
//const urlParams = new URLSearchParams(window.location.search);
//const gameId = urlParams.get('gameId');
let game = new TicTacToeGame();
game.board.drawBoard();
document.body.addEventListener("mousedown", mouseClicked);
//document.body.addEventListener("mousemove", mouseClicked);
