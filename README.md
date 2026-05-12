# Chess Game Engine
This project is a Python-based chess game engine that supports basic chess gameplay, including special moves like pawn promotion, en passant, and castling. It is designed for those interested in how chess engines work and serves as a foundation for further development, such as integrating more advanced AI.

This was done as part of my 12th grade project, with the AI being done as part of a Fundamentals of Programming project in the 1st semester.

## Features
###### Complete implementation of all chess rules:
- Pawn promotion, en passant, and castling
- Check and checkmate detection
- Stalemate detection
- Undo move and reset game

###### AI
- Minimax Algorithm with Alpha-Beta Pruning: This decision-making process evaluates potential moves by looking ahead several steps and assuming optimal play from both sides. Alpha-beta pruning is used to significantly reduce the number of nodes evaluated, improving efficiency.
- Time-Limited Iterative Deepening: The AI keeps deepening while its time budget allows, then plays the best move from the deepest completed search.
- Move Ordering and Quiescence Search: Captures, promotions, checks, and castling are searched first, while tactical capture sequences are extended to reduce horizon-effect blunders.
- Transposition Table: Repeated positions are cached so equivalent move orders do not need to be searched from scratch.
- Opening Book: A small built-in opening book gives the AI principled early-game moves before search takes over.
- Positional Scoring: Beyond simple piece valuation, the AI also considers piece-square tables, mobility, king safety, and pawn structure. This encourages smarter positioning and tactical play.
- Difficulty Levels: Easy, medium, and hard settings adjust randomness, depth, time budget, and search features.


## Potential Improvements
While the current AI is much stronger than the first version, several enhancements could further improve its performance and make the game experience more enriching:

- Larger Opening Book: Expanding the built-in opening lines would improve variety and early-game accuracy.
- Endgame Tablebases: Incorporating endgame tablebases for common endgame positions with limited pieces could enable the AI to play these phases perfectly.
- Machine Learning Techniques: Applying machine learning could allow the AI to learn from past games and adjust its strategy based on successful patterns.
- Parallel Processing: Utilizing parallel processing inside the search could significantly speed up move evaluation, allowing for deeper searches within the same time constraints.
