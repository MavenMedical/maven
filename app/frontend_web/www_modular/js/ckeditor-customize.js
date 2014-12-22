define(['ckeditor2'], function() {
    console.log(CKEDITOR)
    CKEDITOR.config.removeButtons = 'Flash,PageBreak,Iframe,Form,Checkbox,Radio,TextField,Textarea,Select,Button,ImageButton,HiddenField,Save,NewPage,Templates,Print,Preview'
    return CKEDITOR
})
