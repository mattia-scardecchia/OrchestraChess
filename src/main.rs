mod accumulator;
mod board;
mod book;
mod engine;
mod evaluation;
mod magic;
mod move_manager;
mod muve;
mod nnue;
mod orchestradirector;
mod tests;
mod timer;
mod utils;
mod zobrist;

use std::env;
use std::io;

fn main() {
    let args: Vec<String> = env::args().collect();
    let use_book = args.len() > 1 && args[1] == "use-book";
    let mut orchestra_director = orchestradirector::new_orchestra_director(use_book);

    loop {
        let mut message = String::new();

        // Read input from the user
        io::stdin()
            .read_line(&mut message)
            .expect("Failed to read input");

        let message = message.trim(); // Remove trailing newline

        // Split the message into command and options
        let mut parts = message.splitn(2, ' ');
        let command = parts.next().unwrap_or("");
        let options = parts.next().unwrap_or("");

        // Call a function to handle the command
        orchestra_director.handle_command(command, options);
    }
}
