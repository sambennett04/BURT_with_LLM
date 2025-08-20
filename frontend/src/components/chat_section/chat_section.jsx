import React from 'react';
import ChatWindow from './chat_window/chat_window';
import TextInput from './text_input/text_input'
//import ScreenSelector from './screen_selector'

//{showScreens && (<ScreenSelector options={["A", "B", "C"]} onSelect={onScreenSelect} />)}
//when adding screen selection back in, place the above line between ChatWindow and TextInput and put showScreens back in the props list

function ChatSection({ messages, onSubmit, onScreenSelect }) {
  return (
    <div className="chat-section">
      <ChatWindow messages={messages} />
      <TextInput onSubmit={onSubmit} />
    </div>
  );
}

export default ChatSection;