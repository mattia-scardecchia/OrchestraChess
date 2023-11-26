#[cfg(test)]
mod test_move_gen {
    use crate::board::Board;

    fn init_board() -> Board {
        let mut board = Board::empty_board();
        board.from_startpos();
        board
    }

    #[test]
    fn test_move_gen() {
        let data = [("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
                     [1, 20, 400, 8902, 197281, 4865609, 119060324]),
            ("r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1",
             [1, 48, 2039, 97862, 4085603, 193690690, 8031647685]),
            ("8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1",
             [1, 14, 191, 2812, 43238, 674624, 11030083]),
            ("r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1",
             [1, 6, 264, 9467, 422333, 15833292, 0]),
            ("rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8",
             [1, 44, 1486, 62379, 2103487, 89941194, 0]),
            ("r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1 w - - 0 10 ",
             [1, 46, 2079, 89890, 3894594, 164075551, 6923051137])];
        let mut board = Board::empty_board();

        for x in data.iter() {
            let fen = x.0;
            let moves = x.1;
            board.from_fen(fen);
            for i in 0..moves.len() {
                if moves[i] == 0 {
                    continue;
                }
                if i > 5 {
                    continue;
                }
                let result = board.perft(i as i32, -1, true);
                assert_eq!(result, moves[i]);
            }
        }
    }
}
