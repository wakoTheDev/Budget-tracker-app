 // Enhanced Dynamic Content Loader 
 const mymenuItems = document.querySelectorAll("#choices li"); 
 const mycontentDiv = document.getElementById("content-div"); 
 function executeScripts(content) { 
    // Create a temporary div to parse the content 
    const tempDiv = document.createElement('div'); 
    tempDiv.innerHTML = content; 
    // Extract and execute scripts 
    const scripts = tempDiv.getElementsByTagName('script'); 
    for (let script of scripts) { 
        const newScript = document.createElement('script'); 
        // Copy script attributes 
        for (let attr of script.attributes) {
             newScript.setAttribute(attr.name, attr.value); 
            } // Set script content 
            if (script.textContent) { 
                try { 
                    // Wrap in an IIFE to provide a clean execution context 
                    newScript.textContent = (function() { 
                        `${script.textContent} `
                    })();; 
                } catch (error) { 
                    console.error('Error processing script:', error); 
                } 
            } // Append to document to execute 
            document.body.appendChild(newScript); 
            // Remove the script to prevent duplicate executions 
            document.body.removeChild(newScript); } } 
            function loadDynamicContent(page) { 
                fetch(`/get_nav_content/${page}/`) 
                .then(response => response.text()) 
                .then(data => { 
                    // Update content 
                    mycontentDiv.innerHTML = data; 
                    // Execute any scripts in the loaded content 
                    executeScripts(data); }) 
                    .catch(error => { mycontentDiv.innerHTML = `Sorry, there was an error loading the content ${error}`; 
                        console.error('Content loading error:', error); }); 
                    }
                     // Attach event listeners to menu items 
                     mymenuItems.forEach((item )=> {
                         item.addEventListener("click", () => { 
                            const page = item.getAttribute("data-page");
                            console.log("Menu item clicked:", page); 
                            loadDynamicContent(page); });
                         }); 
                         // Fallback: Ensure scripts are loaded even if dynamically inserted 
                         function ensureScriptExecution() { 
                            const dynamicScripts = document.querySelectorAll('script[data-dynamic="true"]'); 
                            dynamicScripts.forEach(script => { 
                                try { 
                                    // Re-execute script content 
                                    const newScript = document.createElement('script'); 
                                    newScript.textContent = script.textContent; 
                                    document.body.appendChild(newScript); 
                                    document.body.removeChild(newScript); 
                                }catch (error) {
                                     console.error('Script re-execution error:', error);
                                     } 
                                    }); 
                                } 
                                // Add event listener to run after content loads 
document.addEventListener('DOMContentLoaded', () => { ensureScriptExecution(); });

