function ScreenSelector({ options, onSelect }){
    return (
        <div className="screen-selector">
            {options.map((opt, idx) => (
                <button key={idx} onClick={() => onSelect(opt)}>
                    {opt}
                </button>
            ))}
        </div>
    );
}

export default ScreenSelector