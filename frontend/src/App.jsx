import { useState } from 'react'
import React from 'react'
import './App.css'
//import ScreenSelector from './components/screen_selector/screen_selector'
import Dropdown from './components/app_selection_dropdown/Dropdown/Dropdown'
import DropdownItem from './components/app_selection_dropdown/DropdownItem/dropdown_item'
import ChatSection from './components/chat_section/chat_section'

function App() {
  const [messages, setMessages] = useState([]);
  
  const [app, setApp] = useState('App Selection');
  const [generatedReport, setGeneratedReport] = useState("");

  //const [showScreens, setShowScreens] = useState(false);
  //when adding screen selection back in, uncomment above line and put showScreens = showScreens back in prop list for showChatWindow

  const [showChatWindow, setShowChatWindow] = useState(false);
  const apps = ['Wikimedia Commons','place_holder','place_holder','place_holder','place_holder'];

  const name_id_map = new Map();
  name_id_map.set('Wikimedia Commons', '135')
  name_id_map.set('place_holder', '0')
  
  const handleUserMessage = (text) => {
    //when a new user message is recieved, make a new user message object to add to the messages list
    const userMsg = {sender: 'user', text};
    const aiMsg = { sender: 'ai', text: "Thanks for your description. Please wait a moment while I generate your complete bug report."};

    //create a new updated messages list containing the userMsg and the aiMsg
    const updatedMessages = [...messages, userMsg, aiMsg];
    
    //update the ui components
    setMessages(updatedMessages);

    //send the update message list to fetchReport, this is neccessary because setMessages gets scheduled after fetchReport
    fetchReport(app, updatedMessages);
    //setShowScreens(true);
  }

  const handleScreenSelect = (option) => {
    const selectionMsg = {sender: 'user', text: `${option}`}
    setMessages(prev => [...prev, selectionMsg]);
    //setShowScreens(false);
  }

  //clear messages everytime app change
  const handleAppSelect = (app) => {
    setApp(app);
    //reset messages when the selected application is changed
    setMessages([]);
    setShowChatWindow(true);
  }

  async function fetchReport(app, messages){

    //add the application selection to the list of messages being sent to the LLM
    const all_messages = [{sender: "user", text: app}, ...messages];

    console.log(JSON.stringify({ messages: all_messages }, null, 2));

    const api_response = await fetch("http://localhost:8000/generateReport", 
      {
      //type of API call
      method: "POST",
      //meta graph_data informing the backend of the type of graph_data it is recieving
      headers: {"Content-Type": "application/json"},
      //body of the post request, what is sent to the backend
      //{ messages } wraps my message inside of a messages object
      body: JSON.stringify({ messages: all_messages })
      }
    );

    //convert api reponse into json formatting
    const report = await api_response.json();

    //set the generated report using the useState method to auto update the componenent holding the report from empty to full
    console.log("Report:", report);
    console.log("Type of report:", typeof report);
    console.log("Report.body:", report.body);

    setGeneratedReport(report.body);

  }

  //need logic that on message to LLM, make new list that concats app selection to beginning of list, messages in middle, screen selection at end. Then send through API

  //notes on adding clickable drop down item, () => defines a new function which is equivalent to running habndleAppSelect with the input Selected App is [user choice]
  return (
    <main className="main-div">
      <div className='interactive-window'>
        <Dropdown 
          buttonText = {app} 
          content ={
          <>
            {apps.map((app, index) => (
              <DropdownItem key={index} onClick={() => handleAppSelect(`${app}`)}> 
                {`${app}`}
              </DropdownItem>))}
          </>
          }
        />
        {showChatWindow && (<ChatSection messages={messages} onSubmit={handleUserMessage} onScreenSelect={handleScreenSelect} />)}
      </div>
      <div className='report-window'>
          <h1 className='report-window-header'>Generated Report:</h1>
          <pre>{generatedReport}</pre>
      </div>
    </main>
  )
}

export default App
