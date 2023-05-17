const messageForm = document.getElementById('message-form');
const messageInput = document.getElementById('message-input');
const messageList = document.getElementById('message-list');

let selectedOption = 'Common_Prompt'; // 默认选中的选项

// 添加选项点击事件处理程序
const promptOption = document.getElementById('prompt-option');
const chainOption = document.getElementById('chain-option');
const searchOption = document.getElementById('search-option');
const keyOption = document.getElementById('keyword-option');

promptOption.addEventListener('click', function(event) {
  event.preventDefault();
  selectedOption = 'Common_Prompt';
  setActiveOption(this); // 设置选项为选中状态
});

chainOption.addEventListener('click', function(event) {
  event.preventDefault();
  selectedOption = 'Chain_of_Thought';
  setActiveOption(this); // 设置选项为选中状态
});

searchOption.addEventListener('click', function(event) {
  event.preventDefault();
  selectedOption = 'Search_in_Chain';
  setActiveOption(this); // 设置选项为选中状态
});

keyOption.addEventListener('click', function(event) {
    event.preventDefault();
    selectedOption = 'Keyword_Search';
    setActiveOption(this); // 设置选项为选中状态
});

messageForm.addEventListener('submit', (event) => {
  event.preventDefault();
  const message = messageInput.value;
  messageInput.value = '';

  const userBubble = createBubble(message, 'user');
  messageList.appendChild(userBubble);
  showLoading();

  fetch(`/api/chat?option=${encodeURIComponent(selectedOption)}`, { // 发送选项到后端API
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ message: message })
  })
    .then((response) => response.json())
    .then((data) => {
      const botBubble = createBubble(data.response, 'bot');
      hideLoading();
      messageList.appendChild(botBubble);
    })
    .catch((error) => console.error(error));
});




function createBubble(message, type) {
  const bubble = document.createElement('div');
  bubble.classList.add('message-bubble');
  bubble.classList.add(type);

  const avatarContainer = document.createElement('div');
  avatarContainer.classList.add('avatar-container');
  avatarContainer.style.flexDirection = 'column';

  const avatar = document.createElement('img');
  avatar.classList.add('message-avatar');
  avatar.src = type === 'user' ? '/static/avatar/user.jpg' : '/static/avatar/bot.png';
  avatar.style.alignSelf = 'flex-start';
  const bubbleContent = document.createElement('div');
  bubbleContent.classList.add('bubble-content');
  bubbleContent.style.alignSelf = 'flex-start';

  const text = document.createElement('div');
  text.classList.add('message-text');
  text.textContent = message;

  avatarContainer.appendChild(avatar);
  bubble.appendChild(avatarContainer);
  bubble.appendChild(bubbleContent);
  bubbleContent.appendChild(text);

  return bubble;
}

// 显示动画
function showLoading() {
  document.getElementById("loading").style.display = "flex";
}

// 隐藏动画
function hideLoading() {
  document.getElementById("loading").style.display = "none";
}

window.addEventListener('DOMContentLoaded', () => {
  // 模拟机器人自动发送消息
  setTimeout(() => {
    const greeting = "你好，我是你的Notion笔记助手，你可以问我关于你的Notion笔记的问题";
    const botBubble = createBubble(greeting, 'bot');
    messageList.appendChild(botBubble);
  }, 500); // 延迟 500ms 发送
  setActiveOption(promptOption); // 设置选项为选中状态
});

// 设置选项为选中状态
function setActiveOption(option) {
  // 移除之前选中的选项的类
  const activeOption = document.querySelector('.options li a.active');
  if (activeOption) {
    activeOption.classList.remove('active');
  }

  // 添加选中状态的类到当前选项
  option.classList.add('active');
}