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
- Positional Scoring: Beyond simple piece valuation, the AI also considers the positions of pieces, with specific scoring grids for different pieces. This encourages smarter positioning and tactical play.


## Potential Improvements
While the current AI provides a solid foundation for 7 year old me, several enhancements could further improve its performance and make the game experience more enriching:

- Dynamic Depth Adjustment: Adjusting the search depth based on the complexity of the position or the stage of the game could improve performance and decision-making.
- Opening Book: Implementing an opening book would allow the AI to play the initial phase of the game based on established theory, potentially leading to stronger play.
- Endgame Tablebases: Incorporating endgame tablebases for common endgame positions with limited pieces could enable the AI to play these phases perfectly.
- Machine Learning Techniques: Applying machine learning could allow the AI to learn from past games and adjust its strategy based on successful patterns.
- Parallel Processing: Utilizing parallel processing could significantly speed up the minimax search, allowing for deeper searches within the same time constraints.
