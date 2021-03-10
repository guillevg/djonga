class Game {
    constructor() {
        this.spectator = true;
        this.me = '';
        this.moveList = '';
        this.waitingForPlayers = true;
        this.inProgress = null;
        this.aborted = null;
        this.winner = null;
        this.currentTurn = Game.O;
        this.movesMade = 0;
        this.squares = new Array(9).fill().map( s => new Square() );
    }

    makeMove(i) {
        //console.log('iiii=' + i);
        //console.log(this.inProgress, this.squares, this.currentTurn, this.me);
        if (this.inProgress && !this.squares[i].value) {
            this.squares[i].value = this.currentTurn;
            this.movesMade++;
            this.checkForWinner();
            this.currentTurn = (this.currentTurn === Game.O) ? Game.X : Game.O;
            return true;
        }
        return false;
    }

    checkForWinner() {
        const winningCombinations = [
            [0, 1, 2],
            [3, 4, 5],
            [6, 7, 8],
            [0, 3, 6],
            [1, 4, 7],
            [2, 5, 8],
            [0, 4, 8],
            [2, 4, 6]
        ];
        winningCombinations.forEach( (wc) => {
            const [a, b, c] = wc;
            const sqA = this.squares[a];
            const sqB = this.squares[b];
            const sqC = this.squares[c];

            if (sqA.value && sqA.value === sqB.value && sqB.value === sqC.value) {
                this.winner = sqA.value;
                this.inProgress = false;
                sqA.isHighlighted = sqB.isHighlighted = sqC.isHighlighted = true;
                console.log(this.winner + " WINS!");
            }

            if (this.movesMade === this.squares.length) {
                this.inProgress = false;
                console.log("TIE");
            }
        })
    }
}

Game.O = 'O';
Game.X = 'X';
