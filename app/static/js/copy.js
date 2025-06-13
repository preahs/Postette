document.addEventListener('DOMContentLoaded', function() {
  const copyButtons = document.querySelectorAll('.copy-button');
  
  copyButtons.forEach(button => {
    button.addEventListener('click', async function() {
      const linkContainer = this.closest('.invite-link-container');
      const link = linkContainer.querySelector('.invite-link').textContent;
      
      try {
        await navigator.clipboard.writeText(link);
        
        // Visual feedback
        this.classList.add('copied');
        const originalText = this.innerHTML;
        this.innerHTML = '<svg><use xlink:href="#check-icon"></use></svg>';
        
        // Reset after 2 seconds
        setTimeout(() => {
          this.classList.remove('copied');
          this.innerHTML = originalText;
        }, 2000);
      } catch (err) {
        console.error('Failed to copy text: ', err);
      }
    });
  });
}); 