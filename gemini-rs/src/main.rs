use std::env;
use reqwest;
use serde_json::{json, Value};
use clap::{Parser, Subcommand};

#[derive(Parser)]
#[command(author, version, about, long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Query the model
    Q {
        /// The query string
        query: Vec<String>,
    },
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let cli = Cli::parse();

    let api_key = env::var("GEMINI_API_KEY").expect("GEMINI_API_KEY not set");
    let api_url = format!("https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={}", api_key);

    match &cli.command {
        Commands::Q { query } => {
            let query_text = query.join(" ");

            let client = reqwest::Client::new();
            let data = json!({
                "contents": [
                    {
                        "parts": [
                            {
                                "text": query_text
                            }
                        ]
                    }
                ]
            });

            let res = client.post(&api_url)
                .json(&data)
                .send()
                .await?;

            let response_json: Value = res.json().await?;
            println!("{}", serde_json::to_string_pretty(&response_json)?);
        }
    }

    Ok(())
}
