package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"sync"
	"time"
)

type ScanResult struct {
	Endpoint   string            `json:"endpoint"`
	Method     string            `json:"method"`
	StatusCode int               `json:"status_code"`
	ResponseMs int64             `json:"response_ms"`
	Headers    map[string]string `json:"headers"`
}

func probe(wg *sync.WaitGroup, results chan<- ScanResult, base, path, method string) {
	defer wg.Done()
	client := &http.Client{Timeout: 5 * time.Second}
	req, _ := http.NewRequest(method, base+path, nil)
	start := time.Now()
	resp, err := client.Do(req)
	if err != nil {
		fmt.Printf("[ERROR] %s %s: %v\n", method, base+path, err)
		return
	}
	defer resp.Body.Close()

	headers := map[string]string{}
	for k, v := range resp.Header {
		headers[k] = v[0]
	}

	results <- ScanResult{
		Endpoint:   base + path,
		Method:     method,
		StatusCode: resp.StatusCode,
		ResponseMs: time.Since(start).Milliseconds(),
		Headers:    headers,
	}
}

func main() {
	target := "https://jsonplaceholder.typicode.com"
	paths := []string{"/posts", "/users", "/comments", "/todos", "/albums"}
	methods := []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"}

	results := make(chan ScanResult, 100)
	var wg sync.WaitGroup

	for _, p := range paths {
		for _, m := range methods {
			wg.Add(1)
			go probe(&wg, results, target, p, m)
		}
	}

	go func() { wg.Wait(); close(results) }()

	var all []ScanResult
	for r := range results {
		all = append(all, r)
		fmt.Printf("[%d] %s %s (%dms)\n", r.StatusCode, r.Method, r.Endpoint, r.ResponseMs)
	}

	out, _ := json.MarshalIndent(all, "", "  ")
	err := os.WriteFile("../results.json", out, 0644)
	if err != nil {
		fmt.Println("[ERROR] Failed to write results.json:", err)
	} else {
		fmt.Println("\n[+] Results saved to results.json")
	}
}
