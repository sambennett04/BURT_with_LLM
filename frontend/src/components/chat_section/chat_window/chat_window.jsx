import React from "react";
import './chat_window.css'

function ChatWindow({ messages }) {
    //this loops over every array item and returns one message component for each message in messages
    //messages are assigned classNames based on the sender meta graph_data attatched to them
    //messages are assigned a unique key so that react can identify which items in the list have changed between renders of the components

    return (
        < div className="chat-window"> 
            {messages.map((msg, idx) => (
                <div key={idx} className={`response ${msg.sender}`}>
                    {msg.text}
                </div>
            ))

            }
        </div>
    );
}

export default ChatWindow