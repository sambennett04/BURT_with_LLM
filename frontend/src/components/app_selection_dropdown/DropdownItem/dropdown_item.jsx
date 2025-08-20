import React from 'react'
import {useState} from 'react'
import './dropdown_item.css'

const DropdownItem = ({ children, onClick }) => {

    return (
        <div className='dropdown-item' onClick = {onClick}>
            {children}
        </div>
    );
};

export default DropdownItem