document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  document.querySelector(`#compose-form`).addEventListener('submit', function(event) {
  event.preventDefault();
  fetch('/emails', {
  method: 'POST',
  body: JSON.stringify({
      recipients: document.querySelector(`#compose-recipients`).value,
      subject: document.querySelector(`#compose-subject`).value,
      body: document.querySelector(`#compose-body`).value
  })
  })
  .then(response => response.json())
  .then(result => {
      load_mailbox('sent');
  });
})

  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';
  document.querySelector('#email-detail').style.display = 'none';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-detail').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {

    emails.forEach(email => {

      const element = document.createElement('div');
      element.innerHTML = `
      <div style="display: flex; justify-content: space-between;">
        <strong>${email.sender}</strong>
        <small style="color: #888;">${email.timestamp}</small>
      </div>
      <div>${email.subject}</div>
      `;
      element.className = 'email-item'
      element.style.backgroundColor = email.read ? '#f0f0f0' : 'white';
      element.onclick = function() {
        fetch(`/emails/${email.id}`)
        .then(response => response.json())
        .then(email => {
          document.querySelector('#email-detail').style.display = 'block';
          document.querySelector('#compose-view').style.display = 'none';
          document.querySelector('#emails-view').style.display = 'none';
          const element = document.createElement('div');
          element.className = 'email-detail';
          element.innerHTML = `
          <div>
            <h3>${email.subject}</h3>
            <p><strong>From:</strong> ${email.sender}</p>
            <p><strong>Time:</strong>${email.timestamp}</p>
            <p><strong>To:</strong> ${email.recipients}</p>
            <hr>
            <p>${email.body}</p>
          </div>
          `;
          document.querySelector('#email-detail').innerHTML = '';
          document.querySelector('#email-detail').append(element);
          if (mailbox !== 'sent') {

            const archiveBtn = document.createElement('button');
            archiveBtn.className = 'btn btn-sm btn-outline-primary';
            if (email.archived === true) {

              archiveBtn.innerHTML = 'Unarchive';
            }
            else {

              archiveBtn.innerHTML = 'Archive';
            };
            archiveBtn.onclick = function() {

              fetch(`/emails/${email.id}`, {
                method: 'PUT',
                body: JSON.stringify({
                  archived: !email.archived
                })
              })
              .then(() => load_mailbox('inbox'));
            };
            document.querySelector('#email-detail').append(archiveBtn);
          }

          const replyBtn = document.createElement('button');
          replyBtn.innerHTML = 'Reply';
          replyBtn.className = 'btn btn-sm btn-outline-primary';
          replyBtn.onclick = function() {

            compose_email();
            document.querySelector('#compose-recipients').value = email.sender;
            if (!email.subject.startsWith('Re:')) {
              document.querySelector('#compose-subject').value = `Re: ${email.subject}`;
            }
            else {
              document.querySelector(`#compose-subject`).value = email.subject;
            }
            document.querySelector('#compose-body').value = `On ${email.timestamp} ${email.sender} wrote: ${email.body}`;
          }
          document.querySelector('#email-detail').append(replyBtn);
          
          fetch(`/emails/${email.id}`, {
            method: 'PUT',
            body: JSON.stringify({
              read: true
            })
          });
        });
      };
      document.querySelector('#emails-view').append(element);
    });
  })}
