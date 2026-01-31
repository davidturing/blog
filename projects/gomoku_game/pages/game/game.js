Page({
    data: {
        board: [], // 15x15 board
        currentTurn: 'black', // 'black' or 'white'
        winner: null,
        lastMove: null, // {x, y}
        gameOver: false,
        boardSize: 15
    },

    onLoad() {
        this.resetGame();
    },

    resetGame() {
        const size = this.data.boardSize;
        const newBoard = Array(size).fill(0).map(() => Array(size).fill(0));
        this.setData({
            board: newBoard,
            currentTurn: 'black',
            winner: null,
            lastMove: null,
            gameOver: false
        });
    },

    onPlacePiece(e) {
        if (this.data.gameOver) return;

        const { x, y } = e.currentTarget.dataset;
        const board = this.data.board;

        if (board[y][x] !== 0) {
            return; // Already occupied
        }

        const currentPlayerValue = this.data.currentTurn === 'black' ? 1 : 2;
        const nextTurn = this.data.currentTurn === 'black' ? 'white' : 'black';

        // Update board safely
        const rowStr = `board[${y}][${x}]`;
        this.setData({
            [rowStr]: currentPlayerValue,
            currentTurn: nextTurn,
            lastMove: { x, y }
        });

        if (this.checkWin(x, y, currentPlayerValue)) {
            this.setData({
                winner: this.data.currentTurn,
                gameOver: true
            });
            wx.showToast({
                title: `${this.data.currentTurn === 'black' ? '黑棋' : '白棋'} 获胜!`,
                icon: 'success',
                duration: 2000
            });
        }
    },

    checkWin(x, y, playerValue) {
        const board = this.data.board;
        const size = this.data.boardSize;

        // Directions: Horizontal, Vertical, Diagonal (\), Diagonal (/)
        const directions = [
            [[1, 0], [-1, 0]],   // Horizontal
            [[0, 1], [0, -1]],   // Vertical
            [[1, 1], [-1, -1]],  // Diagonal \
            [[1, -1], [-1, 1]]   // Diagonal /
        ];

        for (const axis of directions) {
            let count = 1; // Current piece counts as 1

            for (const dir of axis) {
                let dx = dir[0];
                let dy = dir[1];
                let nx = x + dx;
                let ny = y + dy;

                while (
                    nx >= 0 && nx < size &&
                    ny >= 0 && ny < size &&
                    board[ny][nx] === playerValue
                ) {
                    count++;
                    nx += dx;
                    ny += dy;
                }
            }

            if (count >= 5) return true;
        }

        return false;
    }
});
