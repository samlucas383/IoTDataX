import React from 'react';

const Checkbox = () => {
    const [isChecked, setIsChecked] = React.useState(false);

    const handleCheckboxChange = (event) => {
        setIsChecked(event.target.checked);
    };
    
    return (
        <div className="form-check">
            <input 
                className="form-check-input" 
                type="checkbox" 
                checked={isChecked} 
                onChange={handleCheckboxChange}
                id="bootstrapCheckbox"
            />
            <label className="form-check-label" htmlFor="bootstrapCheckbox">
                {isChecked ? 'Checked ✓' : 'Unchecked'}
            </label>
        </div>
    );
}

export default Checkbox;
