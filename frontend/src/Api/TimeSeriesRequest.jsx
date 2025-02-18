export async function TimeSeriesRequest(features) {
    const API_URL = ''

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          data: features
        }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to fetch prediction");
      }
      return await response.json();

    } catch (error) {
      console.error("Error:", error);
      return { prediction: "Error occurred" };
    }
  }
