$(document).ready(function () {
  const searchInput = $("#searchInput");
  const autocompleteResults = $("#autocompleteResults");

  searchInput.on("input", function () {
    const query = $(this).val();

    if (query.trim() === "") {
      autocompleteResults.empty();
      return;
    }

    // Validate input string before perform requests
    if (query.trim().length < 3) {
      return;
    }

    const endpoint = "http://127.0.0.1:5000/autocomplete";
    const esQuery = {
      text: searchInput.val(),
    };

    $.ajax({
      url: endpoint,
      type: "POST",
      contentType: "application/json",
      data: JSON.stringify({
        text: searchInput.val(),
      }),
      success: function (data) {
        displayResults(data);
        console.log(data);
      },
      error: function (error) {
        console.error("Error fetching autocomplete results:", error);
      },
    });
  });

  function displayResults(results) {
    autocompleteResults.empty();

    results.forEach((result) => {
      const source = result._source;
      const listItem = $("<li>").text(source.title);
      listItem.appendTo(autocompleteResults);

      // Handle click event for the result item
      listItem.on("click", function () {
        searchInput.val(source.title);
        autocompleteResults.empty();
      });
    });
  }

  // Handle clicks outside the autocomplete results to close the dropdown
  //   $(document).on("click", function (event) {
  //     if (!$(event.target).closest(".autocomplete-container").length) {
  //       autocompleteResults.empty();
  //     }
  //   });
});
