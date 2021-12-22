$.material.init();

var json = {
 pages: [
  {
   elements: [
    {
     type: "html",
     html: "Hello\n<b> Testing out formatting </b>",
     name: "question1"
    }
   ],
   name: "page6"
  },
  {
   elements: [
    {
     type: "matrix",
     name: "Quality",
     title: "Please indicate if you agree or disagree with the following statements",
     columns: [
      {
       value: 1,
       text: "Strongly Disagree"
      },
      {
       value: 2,
       text: "Disagree"
      },
      {
       value: 3,
       text: "Neutral"
      },
      {
       value: 4,
       text: "Agree"
      },
      {
       value: 5,
       text: "Strongly Agree"
      }
     ],
     rows: [
      {
       value: "affordable",
       text: "Product is affordable"
      },
      {
       value: "does what it claims",
       text: "Product does what it claims"
      },
      {
       value: "better then others",
       text: "Product is better than other products on the market"
      },
      {
       value: "easy to use",
       text: "Product is easy to use"
      }
     ]
    }
   ],
   name: "page1"
  },
  {
   elements: [
    {
     type: "checkbox",
     name: "words",
     title: "Which of the words would you use to describe our products?",
     isRequired: true,
     choices: [
      "Reliable",
      "High quality",
      "Useful",
      "Unique",
      "Good",
      "Overpriced",
      "Impractical",
      "Ineffective",
      "Poor quality",
      "Unreliable",
      "Not for me"
     ],
     colCount: 2
    }
   ],
   name: "page2"
  },
  {
   elements: [
    {
     type: "rating",
     name: "satisfaction",
     title: "How satisfied are you with the Product?",
     minRateDescription: "Not Satisfied",
     maxRateDescription: "Completely satisfied"
    },
    {
     type: "rating",
     name: "recommend friends",
     visible: false,
     visibleIf: "{satisfaction} > 3",
     title: "How likely are you to recommend the Product to a friend or co-worker?",
     minRateDescription: "Will not recommend",
     maxRateDescription: "I will recommend"
    },
    {
     type: "comment",
     name: "suggestions",
     title: "What would make you more satisfied with the Product?"
    }
   ],
   name: "page3"
  },
  {
   elements: [
    {
     type: "radiogroup",
     name: "price to competitors",
     title: "Compared to our competitors, do you feel the Product is",
     choices: [
      "Less expensive",
      "Priced about the same",
      "More expensive",
      "Not sure"
     ]
    },
    {
     type: "radiogroup",
     name: "price",
     title: "Do you feel our current price is merited by our product?",
     choices: [
      {
       value: "correct",
       text: "Yes, the price is about right"
      },
      {
       value: "low",
       text: "No, the price is too low for your product"
      },
      {
       value: "high",
       text: "No, the price is too high for your product"
      }
     ]
    }
   ],
   name: "page4"
  },
  {
   elements: [
    {
     type: "multipletext",
     name: "pricelimit",
     title: "What is the... ",
     items: [
      {
       name: "mostamount",
       title: "The maximum amount you would ever pay for a product like ours"
      },
      {
       name: "leastamount",
       title: "The minimum amount you would feel comfortable paying"
      }
     ]
    },
    {
     type: "text",
     name: "email",
     title: "Thank you for taking our survey. Your survey is almost complete, please enter your email address in the box below if you wish to participate in our drawing, then press the 'Submit' button."
    }
   ],
   name: "page5"
  }
 ],
 showProgressBar: "top",
 title: "Product Feedback Survey Example"
};

Survey.defaultBootstrapMaterialCss.navigationButton = "btn btn-green";
Survey.defaultBootstrapMaterialCss.rating.item = "btn btn-default my-rating";
Survey.Survey.cssType = "bootstrapmaterial";

var survey = new Survey.Model(json);

survey.onComplete.add(function(result) {
var test1 = "prova1";
var test2 = "prova2";
  $.ajax({
    url: "https://docs.google.com/forms/d/e/1FAIpQLSdfXphGVrKYE6X_n7RUAdV_7Aqp9BCdzW174COWJd2eN6yMxg/formResponse",
     headers: { 'Access-Control-Allow-Origin': '*' },
    data: {"entry.1061850032": test1, "entry.902291618": test2},
    type:"POST",
    dataType: "jsonp",
    statusCode: {
      0: function() {
        //Success message
      },
      200: function() {
        //Success Message
      }
    }
  });
	document.querySelector('#result').innerHTML = "result: " + JSON.stringify(result.data);
});

survey.render("surveyElement");
