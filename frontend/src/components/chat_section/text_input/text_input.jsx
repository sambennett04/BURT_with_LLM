import { useState } from 'react';
import './text_input.css'

function TextInput({ onSubmit }) {
    //This const holds the user input, useState will update the component automatically everytime the input is changed
    const [input, setInput] = useState('');

    //When the send button is selected, this method will validate that the user input is not empty and then call the function pointed to by the prop onSubmit, passing the user input to it
    const handleSend = () => {
        if (input.trim() !== '') {
            onSubmit(input);
            setInput('');
        }
    };

    return (
        <div className="text-input">
            <textarea name="text-box" value={input} onChange={(e) => setInput(e.target.value)} placeholder='Describe your Bug' />
            <button className="send-button" onClick={handleSend}>Send</button>
        </div> 
    )

}

export default TextInput