// nodemailerConfig.js
const nodemailer = require('nodemailer');

const transporter = nodemailer.createTransport({
    host: 'smtp.ethereal.email',
    port: 587,
    auth: {
        user: 'magali.upton8@ethereal.email', // Cambia esto por tu usuario de Ethereal
        pass: 'RHf4kZre7rn5R1fzfp' // Cambia esto por tu contraseña de Ethereal
    }
});

module.exports = transporter;
