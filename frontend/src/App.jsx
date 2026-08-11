import { useState } from "react";
import axios from "axios";
import "./App.css";

const API_URL = "http://localhost:8001";

function App() {
  const [file, setFile] = useState(null);
  const [projectId, setProjectId] = useState("");
  const [repositoryName, setRepositoryName] = useState("");

  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);

  const [uploading, setUploading] = useState(false);
  const [asking, setAsking] = useState(false);
  const [error, setError] = useState("");

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a ZIP file first.");
      return;
    }

    setUploading(true);
    setError("");
    setMessages([]);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(
        `${API_URL}/upload/`,
        formData
      );

      setProjectId(response.data.project_id);
      setRepositoryName(response.data.filename);

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Failed to upload the repository."
      );
    } finally {
      setUploading(false);
    }
  };

  const handleAsk = async () => {
    const trimmedQuestion = question.trim();

    if (!projectId) {
      setError("Please upload a repository first.");
      return;
    }

    if (!trimmedQuestion) {
      setError("Please enter a question.");
      return;
    }

    setAsking(true);
    setError("");

    // Add the user's question immediately.
    const userMessage = {
      role: "user",
      content: trimmedQuestion,
    };

    setMessages((previous) => [
      ...previous,
      userMessage,
    ]);

    setQuestion("");

    try {
      // const response = await axios.post(
      //   `${API_URL}/query/`,
      //   {
      //     project_id: projectId,
      //     question: trimmedQuestion,
      //   }
      // );
      const response = await axios.post(
        `${API_URL}/query/`,
        {
          project_id: projectId,
          question: trimmedQuestion,
          conversation: messages.map((message) => ({
            role: message.role,
            content: message.content,
          })),
        }
      );

      const assistantMessage = {
        role: "assistant",
        content: response.data.answer,
        sources: response.data.sources || [],
      };

      setMessages((previous) => [
        ...previous,
        assistantMessage,
      ]);

    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Failed to answer the question."
      );
    } finally {
      setAsking(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();

      if (!asking) {
        handleAsk();
      }
    }
  };

  return (
    <div className="app">

      <header className="header">
        <div>
          <h1>CodeCompass AI</h1>
          <p>
            Understand your software repositories with AI.
          </p>
        </div>
      </header>

      <main className="container">

        {/* Repository upload */}
        <section className="card">

          <div className="section-title">
            <div>
              <h2>Repository</h2>
              <p>
                Upload a ZIP file containing your codebase.
              </p>
            </div>
          </div>

          <div className="upload-area">

            <input
              id="repository-file"
              type="file"
              accept=".zip"
              onChange={(event) => {
                setFile(event.target.files[0]);
                setError("");
              }}
            />

            {file && (
              <p className="selected-file">
                Selected: <strong>{file.name}</strong>
              </p>
            )}

            <button
              onClick={handleUpload}
              disabled={!file || uploading}
            >
              {uploading
                ? "Indexing..."
                : "Upload Repository"}
            </button>

          </div>

          {projectId && (
            <div className="repository-status">

              <span className="status-dot"></span>

              <div>
                <strong>{repositoryName}</strong>

                <p>
                  Repository indexed successfully.
                </p>
              </div>

            </div>
          )}

        </section>

        {/* Chat */}
        <section className="card chat-card">

          <div className="section-title">
            <div>
              <h2>Ask about your code</h2>

              <p>
                Ask questions about implementation, APIs,
                dependencies, and how the repository works.
              </p>
            </div>
          </div>

          {/* Conversation */}
          <div className="conversation">

            {messages.length === 0 && (
              <div className="empty-chat">
                <p>
                  Start by asking a question about your repository.
                </p>

                <div className="suggestions">

                  <button
                    onClick={() =>
                      setQuestion(
                        "Where is the Python code implemented?"
                      )
                    }
                    disabled={!projectId}
                  >
                    Where is the Python code implemented?
                  </button>

                  <button
                    onClick={() =>
                      setQuestion(
                        "What dependencies does this project have?"
                      )
                    }
                    disabled={!projectId}
                  >
                    What dependencies does this project have?
                  </button>

                  <button
                    onClick={() =>
                      setQuestion(
                        "What files are available in this repository?"
                      )
                    }
                    disabled={!projectId}
                  >
                    What files are available?
                  </button>

                </div>
              </div>
            )}

            {messages.map((message, index) => (

              <div
                key={index}
                className={`message ${message.role}`}
              >

                <div className="message-label">
                  {message.role === "user"
                    ? "You"
                    : "CodeCompass"}
                </div>

                <div className="message-content">
                  {message.content}
                </div>

                {message.role === "assistant" &&
                  message.sources?.length > 0 && (

                  <div className="message-sources">

                    <h4>Sources</h4>

                    {message.sources.map(
                      (source, sourceIndex) => (

                      <div
                        className="source"
                        key={`${source.file_path}-${sourceIndex}`}
                      >

                        <div>
                          <strong>
                            {source.file_path}
                          </strong>

                          <span>
                            {source.language}
                          </span>
                        </div>

                      </div>

                    ))}

                  </div>
                )}

              </div>

            ))}

            {asking && (
              <div className="message assistant">

                <div className="message-label">
                  CodeCompass
                </div>

                <div className="typing">
                  Analyzing the repository...
                </div>

              </div>
            )}

          </div>

          {/* Question input */}
          <div className="question-box">

            <textarea
              value={question}
              onChange={(event) =>
                setQuestion(event.target.value)
              }
              onKeyDown={handleKeyDown}
              placeholder={
                projectId
                  ? "Ask a question about your code..."
                  : "Upload a repository first..."
              }
              rows="3"
              disabled={!projectId || asking}
            />

            <div className="input-footer">

              <span>
                Enter to ask · Shift + Enter for a new line
              </span>

              <button
                onClick={handleAsk}
                disabled={
                  !projectId ||
                  !question.trim() ||
                  asking
                }
              >
                {asking ? "Thinking..." : "Ask"}
              </button>

            </div>

          </div>

        </section>

        {error && (
          <div className="error">
            {error}
          </div>
        )}

      </main>

    </div>
  );
}

export default App;