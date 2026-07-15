# PROJECT GENESIS BRANDING TECHNICAL NOTE

The branded launcher wraps the existing Tkinter entry point rather than replacing the application source. It applies the CertiAura title, icon, header and footer and supports root layouts using pack or grid. Branding failures are caught so they do not prevent Project Genesis from opening.

This reduces coupling to the current Project Genesis filename and widget layout.
