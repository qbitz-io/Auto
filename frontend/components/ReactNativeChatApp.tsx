import React, { useState, useEffect } from 'react';
import { SafeAreaView, View, Text, TextInput, Button, FlatList, Modal, TouchableOpacity, StyleSheet, Alert } from 'react-native';

const ChatMessage = ({ message, isUser }) => {
  return (
    <View style={[styles.messageContainer, isUser ? styles.userMessage : styles.botMessage]}>
      <Text style={styles.messageText}>{message}</Text>
    </View>
  );
};

const ApprovalPopup = ({ visible, onApprove, onReject, message }) => {
  return (
    <Modal
      animationType="fade"
      transparent={true}
      visible={visible}
      onRequestClose={onReject}
    >
      <View style={styles.modalOverlay}>
        <View style={styles.modalContent}>
          <Text style={styles.modalMessage}>{message}</Text>
          <View style={styles.modalButtons}>
            <Button title="Approve" onPress={onApprove} />
            <Button title="Reject" onPress={onReject} color="red" />
          </View>
        </View>
      </View>
    </Modal>
  );
};

const ReactNativeChatApp = () => {
  const [apiKey, setApiKey] = useState('');
  const [apiKeySet, setApiKeySet] = useState(false);
  const [inputMessage, setInputMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const [approvalVisible, setApprovalVisible] = useState(false);
  const [pendingMessage, setPendingMessage] = useState(null);

  // Function to send message to Fly instance API
  const sendMessageToFly = async (message) => {
    try {
      const response = await fetch('https://api.fly.io/v1/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${apiKey}`,
        },
        body: JSON.stringify({ message }),
      });
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      const data = await response.json();
      return data.reply || 'No reply from Fly instance';
    } catch (error) {
      return `Error: ${error.message}`;
    }
  };

  const handleSend = () => {
    if (!inputMessage.trim()) return;
    // Show approval popup before sending
    setPendingMessage(inputMessage.trim());
    setApprovalVisible(true);
  };

  const onApprove = async () => {
    setApprovalVisible(false);
    if (!pendingMessage) return;

    // Add user message
    setMessages((prev) => [...prev, { id: Date.now().toString(), text: pendingMessage, isUser: true }]);

    // Send to Fly instance
    const reply = await sendMessageToFly(pendingMessage);

    // Add bot reply
    setMessages((prev) => [...prev, { id: (Date.now() + 1).toString(), text: reply, isUser: false }]);

    setInputMessage('');
    setPendingMessage(null);
  };

  const onReject = () => {
    setApprovalVisible(false);
    setPendingMessage(null);
  };

  const handleSetApiKey = () => {
    if (apiKey.trim()) {
      setApiKeySet(true);
      Alert.alert('API Key Set', 'Your API key has been saved.');
    } else {
      Alert.alert('Error', 'Please enter a valid API key.');
    }
  };

  if (!apiKeySet) {
    return (
      <SafeAreaView style={styles.container}>
        <Text style={styles.title}>Enter your Fly API Key</Text>
        <TextInput
          style={styles.input}
          placeholder="API Key"
          value={apiKey}
          onChangeText={setApiKey}
          secureTextEntry
          autoCapitalize="none"
        />
        <Button title="Set API Key" onPress={handleSetApiKey} />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <FlatList
        data={messages}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => <ChatMessage message={item.text} isUser={item.isUser} />}
        contentContainerStyle={styles.chatContainer}
      />
      <View style={styles.inputContainer}>
        <TextInput
          style={styles.textInput}
          placeholder="Type your message..."
          value={inputMessage}
          onChangeText={setInputMessage}
          onSubmitEditing={handleSend}
          returnKeyType="send"
        />
        <Button title="Send" onPress={handleSend} />
      </View>
      <ApprovalPopup
        visible={approvalVisible}
        onApprove={onApprove}
        onReject={onReject}
        message={`Send this message?\n\n"${pendingMessage}"`}
      />
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    margin: 20,
    textAlign: 'center',
  },
  input: {
    height: 50,
    marginHorizontal: 20,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 8,
    paddingHorizontal: 10,
  },
  chatContainer: {
    padding: 10,
  },
  messageContainer: {
    marginVertical: 5,
    padding: 10,
    borderRadius: 10,
    maxWidth: '80%',
  },
  userMessage: {
    backgroundColor: '#0078fe',
    alignSelf: 'flex-end',
  },
  botMessage: {
    backgroundColor: '#e5e5ea',
    alignSelf: 'flex-start',
  },
  messageText: {
    color: '#fff',
  },
  inputContainer: {
    flexDirection: 'row',
    padding: 10,
    borderTopWidth: 1,
    borderColor: '#ccc',
    backgroundColor: '#fff',
  },
  textInput: {
    flex: 1,
    height: 40,
    borderColor: '#ccc',
    borderWidth: 1,
    borderRadius: 20,
    paddingHorizontal: 15,
    marginRight: 10,
    backgroundColor: '#fff',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 10,
    width: '80%',
    alignItems: 'center',
  },
  modalMessage: {
    fontSize: 16,
    marginBottom: 20,
    textAlign: 'center',
  },
  modalButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    width: '100%',
  },
});

export default ReactNativeChatApp;
