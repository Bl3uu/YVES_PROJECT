using Newtonsoft.Json; // Make sure you installed the NuGet package!
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;

namespace YvesInterface
{
    // Helper class moved outside the MainWindow class for better OOP structure
    public class InventoryState
    {
        public List<string> files { get; set; }
    }

    public partial class MainWindow : Window
    {
        private readonly HttpClient _client = new HttpClient();
        private FileSystemWatcher _watcher;
        private DateTime _lastRead = DateTime.MinValue;

        public MainWindow()
        {
            InitializeComponent();
            _ = RefreshSidebar();
            SetupFileWatcher(); // Initialize the "Observer"
        }

        private async Task RefreshSidebar()
        {
            try
            {
                var response = await _client.GetStringAsync("http://127.0.0.1:8000/list_files");
                var data = JsonConvert.DeserializeObject<InventoryState>(response);

                if (data != null && data.files != null)
                {
                    // Force a UI refresh by setting to null first
                    FileListView.ItemsSource = null;
                    FileListView.ItemsSource = data.files;
                    Debug.WriteLine("UI: Sidebar list updated.");
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"Sidebar Sync Failed: {ex.Message}");
            }
        }

        private async void Sync_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                await _client.PostAsync("http://127.0.0.1:8000/sync", null);
                await RefreshSidebar();
                MessageBox.Show("Yves has finished her audit. Memory is up to date.", "System Update");
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Failed to sync: {ex.Message}");
            }
        }

        // --- THE CHAT LOGIC (ADD THIS NOW) ---

        private async void Send_Click(object sender, RoutedEventArgs e)
        {
            await ProcessChat();
        }

        private async void InputBox_KeyDown(object sender, KeyEventArgs e)
        {
            if (e.Key == Key.Enter)
            {
                await ProcessChat();
            }
        }

        private async Task ProcessChat()
        {
            string userInput = InputBox.Text.Trim();
            if (string.IsNullOrEmpty(userInput)) return;

            AddMessage("You", userInput);
            InputBox.Clear();

            // Disable input while she thinks
            InputBox.IsEnabled = false;

            try
            {
                // (API call logic stays the same...)
                var payload = new { prompt = userInput };
                var json = JsonConvert.SerializeObject(payload);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                var response = await _client.PostAsync("http://127.0.0.1:8000/ask", content);
                var responseString = await response.Content.ReadAsStringAsync();
                var result = JsonConvert.DeserializeObject<dynamic>(responseString);

                AddMessage("Yves", (string)result.reply);
            }
            finally
            {
                // Re-enable input
                InputBox.IsEnabled = true;
                InputBox.Focus();
            }
        }

        private void AddMessage(string sender, string message)
        {
            bool isUser = sender == "You";

            Border bubble = new Border
            {
                Background = isUser ? new SolidColorBrush(Color.FromRgb(0, 122, 204)) : new SolidColorBrush(Color.FromRgb(62, 62, 66)),
                CornerRadius = new CornerRadius(10),
                Padding = new Thickness(10),
                Margin = new Thickness(isUser ? 50 : 10, 5, isUser ? 10 : 50, 5),
                HorizontalAlignment = isUser ? HorizontalAlignment.Right : HorizontalAlignment.Left
            };

            bubble.Child = new TextBlock
            {
                Text = message,
                Foreground = Brushes.White,
                TextWrapping = TextWrapping.Wrap
            };

            ChatDisplay.Children.Add(bubble);
            ChatScroll.ScrollToBottom();
        }

        private void SetupFileWatcher()
        {
            // Ensure this path is 100% identical to your File Explorer path
            string path = @"C:\Users\Dusti\Downloads\Projects\YVES_CORE\data\inventory";

            if (!System.IO.Directory.Exists(path))
            {
                MessageBox.Show("Watcher Error: Path not found!");
                return;
            }

            _watcher = new FileSystemWatcher(path)
            {
                NotifyFilter = NotifyFilters.FileName | NotifyFilters.LastWrite | NotifyFilters.DirectoryName,
                Filter = "*.*",
                IncludeSubdirectories = true, // Added this for extra coverage
                EnableRaisingEvents = true
            };

            _watcher.Changed += OnFileChanged;
            _watcher.Created += OnFileChanged;
            _watcher.Deleted += OnFileChanged;
            _watcher.Renamed += OnFileChanged; // Added Renamed support
        }

        private async void OnFileChanged(object sender, FileSystemEventArgs e)
        {
            if (DateTime.Now.Subtract(_lastRead).TotalMilliseconds < 1000) return; // 1 second cooldown
            _lastRead = DateTime.Now;

            // Use the Dispatcher to ensure we are on the main thread
            await Application.Current.Dispatcher.InvokeAsync(async () =>
            {
                await Task.Delay(500); // Give Windows more time to "release" the file

                try
                {
                    // Force the Sync
                    var syncResponse = await _client.PostAsync("http://127.0.0.1:8000/sync", null);

                    if (syncResponse.IsSuccessStatusCode)
                    {
                        // Force the Sidebar to fetch the new list
                        await RefreshSidebar();
                        Debug.WriteLine("Sidebar refreshed automatically.");
                    }
                }
                catch (Exception ex)
                {
                    Debug.WriteLine($"Auto-update failed: {ex.Message}");
                }
            });
        }
    }
}