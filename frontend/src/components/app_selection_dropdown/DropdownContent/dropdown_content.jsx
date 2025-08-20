import React from 'react';
//import './dropdown_content.css'

const DropdownContent = ( {children, open} ) => {
    return (
        <div className={`dropdown-content ${open ? "content-open" : null}`}>
            {children}
        </div>
    );
};

export default DropdownContent;