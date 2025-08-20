import React from 'react';
import { useState } from 'react'
import DropdownButton from '../DropdownButton/dropdown_button';
import DropdownContent from '../DropdownContent/dropdown_content';
import './dropdown.css'

const Dropdown = ({ buttonText, content }) => {

    const [open, setOpen] = useState(false);

    const toggleDropdown = () => {
        setOpen(open => !open)
    };

    return (
    <div className='dropdown'>
        <DropdownButton toggle = {toggleDropdown} open = {open}>
            {buttonText}
        </DropdownButton>
        {open && <DropdownContent open = {open} >
            {content}
        </DropdownContent>}
    </div>
    );
};

export default Dropdown;