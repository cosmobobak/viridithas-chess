# Chess

A Python chess engine using opening books, principal variation search, the python-chess library, and a hash table for tracking transpositions across different depth searches. The main engine is found within Objective-V.py. Modes for Antichess, Atomic, and Crazyhouse are implemented via subclasses of the main engine, but Crazyhouse currently possesses suboptimal evaluation.
