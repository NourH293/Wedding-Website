<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { AlertTriangle, UserCheck, X, Search, Users, Loader2, Phone, Hash } from 'lucide-vue-next'

// --- CONFIGURATION ---
// Base URL for the self-hosted Django API backend
// IMPORTANT: Update this to your deployed backend URL (e.g., 'https://api.yourdomain.com')
const API_BASE_URL = ''
// API Endpoints
const API_ENDPOINTS = {
  GUESTS: `${API_BASE_URL}/api/guests/`,
  RSVP_UPDATE: `${API_BASE_URL}/api/rsvp/update/`,
}

// Reactive state
const router = useRouter()
const allGuests = ref([])
const searchNameOrPhone = ref('')
const searchResults = ref([])
const selectedHeadGuest = ref(null)
const familyResponse = ref('Attending')
const attendingCount = ref(1) // NEW: Number of people attending
const maxFamilyGuests = ref(0) // NEW: Maximum guests allowed for the family
const isLoading = ref(true)
const showMessage = ref({ type: '', text: '' })
const isRsvpSubmitted = ref(false)

// --- UTILITIES ---

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

/**
 * Sanitizes input string to remove potential script injections or malicious characters.
 * @param {string} input - The raw user input.
 * @returns {string} The sanitized string.
 */
const sanitizeString = (input) => {
  if (!input) return ''
  return input.replace(/<script\b[^>]*>([\s\S]*?)<\/script>/gim, '').replace(/[<>"']/g, (match) => {
    if (match === '<') return '&lt;'
    if (match === '>') return '&gt;'
    if (match === '"') return '&quot;'
    if (match === "'") return '&#x27;'
    return match
  })
}

/**
 * Calculates the Levenshtein distance between two strings (Fuzzy Matching).
 * @param {string} a
 * @param {string} b
 * @returns {number} The distance (number of edits required).
 */
const levenshteinDistance = (a, b) => {
  const an = a ? a.toLowerCase() : ''
  const bn = b ? b.toLowerCase() : ''

  if (an.length === 0) return bn.length
  if (bn.length === 0) return an.length

  const matrix = []

  for (let i = 0; i <= an.length; i++) {
    matrix[i] = [i]
  }

  for (let j = 0; j <= bn.length; j++) {
    matrix[0][j] = j
  }

  for (let i = 1; i <= an.length; i++) {
    for (let j = 1; j <= bn.length; j++) {
      const cost = an[i - 1] === bn[j - 1] ? 0 : 1
      matrix[i][j] = Math.min(
        matrix[i - 1][j] + 1, // deletion
        matrix[i][j - 1] + 1, // insertion
        matrix[i - 1][j - 1] + cost, // substitution
      )
    }
  }

  return matrix[an.length][bn.length]
}

// --- API INTERACTIONS ---

/**
 * Fetches the entire guest list from the Django backend.
 */
const fetchGuestData = async () => {
  isLoading.value = true
  try {
    const response = await fetch(API_ENDPOINTS.GUESTS)

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    allGuests.value = data
    showMessage.value = {
      type: 'info',
      text: `Connected to API. Ready to search among ${data.length} guests.`,
    }
  } catch (error) {
    console.error('Error fetching guest data from API:', error)
    showMessage.value = {
      type: 'error',
      text: `Connection Failed: Could not connect to API at ${API_BASE_URL}. Ensure your Django server is running.`,
    }
  } finally {
    isLoading.value = false
  }
}

/**
 * Searches the guest list using exact phone number or fuzzy name matching.
 */
const handleSearch = () => {
  const rawQuery = searchNameOrPhone.value
  const sanitizedQuery = sanitizeString(rawQuery)
  const query = sanitizedQuery.trim().toLowerCase()

  searchResults.value = []
  selectedHeadGuest.value = null
  showMessage.value = { type: '', text: '' }

  if (query.length < 3) {
    showMessage.value = {
      type: 'info',
      text: 'Please enter at least 3 characters or the phone number.',
    }
    return
  }

  if (allGuests.value.length === 0) {
    showMessage.value = {
      type: 'error',
      text: 'Guest list is empty. Please ensure the backend server has loaded initial data.',
    }
    return
  }

  // Check if the query looks like a phone number (only digits, allowing spaces/dashes for comparison)
  const phoneQuery = query.replace(/[^0-9]/g, '')
  let candidates = []

  if (phoneQuery.length >= 7) {
    // Attempt 1: Exact Phone Number Match (Normalized)
    candidates = allGuests.value.filter(
      (guest) => guest.phoneNumber && guest.phoneNumber.replace(/[^0-9]/g, '') === phoneQuery,
    )

    if (candidates.length === 1) {
      // Direct hit on phone number, auto-select
      selectGuest(candidates[0])
      return
    }
  }

  // Attempt 2: Fuzzy Name Match (only if no exact phone match or query isn't primarily a phone number)
  if (candidates.length === 0 || phoneQuery.length < 7) {
    allGuests.value.forEach((guest) => {
      const fullName = guest.name.toLowerCase()
      const distFullName = levenshteinDistance(fullName, query)

      if (distFullName <= 4) {
        candidates.push({ ...guest, distance: distFullName })
      }
    })

    // Remove duplicates (e.g., if a name match was already included)
    candidates = Array.from(new Set(candidates.map((g) => g.phoneNumber))).map((phoneNumber) =>
      candidates.find((g) => g.phoneNumber === phoneNumber),
    )

    // Sort by distance (best match first)
    candidates.sort((a, b) => (a.distance || 99) - (b.distance || 99))
    const bestCandidates = candidates

    if (bestCandidates.length === 0) {
      showMessage.value = {
        type: 'error',
        text: "Sorry, we couldn't find a match for that name or phone number. Please try checking your spelling or ensure you are using the phone number we have on file.",
      }
      return
    }

    if (bestCandidates.length === 1) {
      // Automatically select the single best match
      selectGuest(bestCandidates[0])
    } else {
      // Show multiple matches for the user to choose
      searchResults.value = bestCandidates
      showMessage.value = {
        type: 'info',
        text: 'Multiple matches found. Please select your name from the list below:',
      }
    }
  }
}

/**
 * Selects a guest (Head of Family) and loads their entire family group.
 * @param {Guest} guest - The selected head-of-family guest object.
 */
const selectGuest = (guest) => {
  selectedHeadGuest.value = guest
  maxFamilyGuests.value = guest.maxGuests || 1

  // Set the initial form response based on the family head's current response
  familyResponse.value = guest.response === 'Pending' ? 'Attending' : guest.response

  // Set initial attending count based on last known state or default to 1
  attendingCount.value =
    guest.attending_count && guest.response === 'Attending' ? guest.attending_count : 1

  searchResults.value = []
  showMessage.value = {
    type: 'success',
    text: `Welcome, ${guest.name}! Please submit your family's RSVP below. Max guests: ${maxFamilyGuests.value}.`,
  }
}

// --- FORM SUBMISSION ---

/**
 * Handles the final submission of the family's RSVP by calling the Django PATCH API.
 */
const submitRsvp = async () => {
  if (!selectedHeadGuest.value) return

  isLoading.value = true
  let response = null
  let result = null

  // 1. Prepare data for the API
  const guest_phoneNumber = selectedHeadGuest.value.phoneNumber
  const newResponse = familyResponse.value

  // Calculate final attending count based on response
  let finalAttendingCount = 0
  if (newResponse === 'Attending') {
    finalAttendingCount = attendingCount.value
  }

  // The API call is to update the entire family group's RSVP status.
  const payload = {
    phoneNumber: guest_phoneNumber,
    response: newResponse,
    // NEW: Send the count as well
    attending_count: finalAttendingCount,
  }

  try {
    // 2. Send PATCH request to the API
    response = await fetch(API_ENDPOINTS.RSVP_UPDATE, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    })

    // CRITICAL FIX: Clone the response so we can read the body multiple times if needed.
    const responseClone = response.clone()

    if (!response.ok) {
      // --- Error Handling ---
      let errorText = `HTTP Error ${response.status} (${response.statusText}).`

      try {
        // Attempt to parse as JSON (for structured API errors)
        const jsonError = await response.json()
        errorText = jsonError.detail || jsonError.message || JSON.stringify(jsonError)
      } catch (e) {
        // If JSON fails, read as plain text/HTML (for 404/500 pages)
        const htmlError = await responseClone.text()

        // Log the full HTML error to the console for detailed debugging
        console.error('Full non-JSON error response (likely HTML):', htmlError)

        // Extract the title of the HTML page if possible to provide context
        const titleMatch = htmlError.match(/<title>(.*?)<\/title>/i)
        const errorTitle = titleMatch ? `: ${titleMatch[1]}` : ''

        errorText = `Server Error ${response.status} (${response.statusText})${errorTitle}. See console for full details.`
      }

      throw new Error(errorText)
    }

    // --- Success Handling ---
    // If response.ok, always read the original response as JSON
    result = await response.json()

    // 3. Update local state to reflect successful submission
    isRsvpSubmitted.value = true
    showMessage.value = {
      type: 'success',
      text: `Thank you, ${selectedHeadGuest.value.name}! Your RSVP has been successfully recorded as ${newResponse} (${finalAttendingCount} attending). Redirecting you to the Home page.`,
    }

    // Reset search state
    searchNameOrPhone.value = ''
    selectedHeadGuest.value = null

    await delay(2000)

    // Re-fetch data to reflect changes immediately across the app
    await fetchGuestData()

    router.push('/')
  } catch (error) {
    console.error('Error submitting RSVP:', error)
    showMessage.value = { type: 'error', text: `Failed to submit RSVP: ${error.message}.` }
  } finally {
    isLoading.value = false
  }
}

// --- LIFECYCLE ---
onMounted(() => {
  fetchGuestData()
})
</script>

<template>
  <div class="min-h-screen bg-gray-50 font-sans text-gray-800 p-4 sm:p-8 relative">
    <div class="max-w-3xl mx-auto py-12 bg-white rounded-xl shadow-2xl border border-pink-100">
      <header class="text-center mb-10 px-6">
        <h1 class="text-5xl font-serif text-pink-600 mb-3">RSVP</h1>
        <p class="text-lg text-gray-600">
          Please search for your name or phone number to confirm attendance.
        </p>
      </header>

      <!-- Loading & Message Area -->
      <div class="px-6 mb-8">
        <!-- Global Loader -->
        <div v-if="isLoading" class="flex items-center justify-center p-4 text-pink-600">
          <Loader2 class="w-6 h-6 animate-spin mr-2" />
          <span v-if="allGuests.length === 0">Connecting to Self-Hosted API...</span>
          <span v-else>Processing Request...</span>
        </div>

        <!-- Status Messages -->
        <div
          v-if="showMessage.text"
          :class="[
            'p-4 rounded-lg flex items-start border',
            showMessage.type === 'error'
              ? 'bg-red-50 text-red-700 border-red-200'
              : showMessage.type === 'success'
                ? 'bg-green-50 text-green-700 border-green-200'
                : 'bg-blue-50 text-blue-700 border-blue-200',
          ]"
        >
          <AlertTriangle
            v-if="showMessage.type === 'error'"
            class="w-5 h-5 mr-3 mt-1 flex-shrink-0"
          />
          <UserCheck
            v-else-if="showMessage.type === 'success'"
            class="w-5 h-5 mr-3 mt-1 flex-shrink-0"
          />
          <Search v-else class="w-5 h-5 mr-3 mt-1 flex-shrink-0" />
          <p class="text-sm font-medium">{{ showMessage.text }}</p>
        </div>
      </div>

      <!-- 1. Search Component -->
      <section v-if="!selectedHeadGuest" class="px-6">
        <form @submit.prevent="handleSearch" class="flex flex-col sm:flex-row gap-4 mb-8">
          <input
            type="text"
            v-model="searchNameOrPhone"
            placeholder="Enter Your Full Name (or Phone Number)"
            class="flex-grow p-3 border border-gray-300 rounded-lg focus:border-pink-500 focus:ring-1 focus:ring-pink-500 transition duration-150"
            :disabled="isLoading"
          />
          <button
            type="submit"
            class="px-6 py-3 bg-pink-600 text-white font-semibold rounded-lg shadow-md hover:bg-pink-700 transition duration-300 flex items-center justify-center"
            :disabled="isLoading || searchNameOrPhone.length < 3"
          >
            <Search class="w-5 h-5 mr-2" /> Find My RSVP
          </button>
        </form>

        <!-- Fuzzy Search Results Selection -->
        <div
          v-if="searchResults.length > 1"
          class="space-y-3 p-4 bg-gray-50 rounded-lg border border-gray-200"
        >
          <p class="font-semibold text-gray-700 flex items-center">
            <Users class="w-4 h-4 mr-2" /> Possible Matches:
          </p>
          <div class="grid gap-2">
            <button
              v-for="guest in searchResults"
              :key="guest.phoneNumber"
              @click="selectGuest(guest)"
              class="w-full text-left p-3 bg-white border border-gray-300 rounded-md hover:bg-pink-50 hover:border-pink-500 transition duration-150 shadow-sm"
            >
              {{ guest.name }} (Phone Number: {{ guest.phoneNumber }})
              <span v-if="(guest.distance || 0) === 0" class="text-green-500 ml-2"
                >(Exact Match)</span
              >
              <span v-else class="text-orange-500 ml-2"
                >(Fuzzy Match: {{ guest.distance }} edit(s))</span
              >
            </button>
          </div>
        </div>
      </section>

      <!-- 2. RSVP Form Component -->
      <section v-else class="px-6">
        <h2 class="text-3xl font-serif text-gray-800 mb-6 border-b pb-2">
          RSVP for {{ selectedHeadGuest.name }} and Family
        </h2>

        <!-- Family Information -->
        <div class="mb-8 p-4 bg-pink-50 border border-pink-200 rounded-lg space-y-3">
          <p class="font-semibold text-pink-700 flex items-center">
            <Users class="w-4 h-4 mr-2" /> Guests in Your Party:
          </p>
          <ul class="list-disc list-inside text-gray-700 ml-4">
            <li>
              {{ selectedHeadGuest.name }}
              <span class="text-xs font-medium text-pink-600">(Family Contact)</span>
              <span
                v-if="selectedHeadGuest.response !== 'Pending'"
                :class="[
                  'ml-2 text-xs font-bold',
                  selectedHeadGuest.response === 'Attending' ? 'text-green-600' : 'text-red-600',
                ]"
              >
                ({{ selectedHeadGuest.response }})
              </span>
            </li>
          </ul>
          <p class="text-sm font-bold text-pink-800 flex items-center">
            <Hash class="w-4 h-4 mr-2" /> Maximum guests allowed: {{ maxFamilyGuests }}
          </p>
        </div>

        <!-- Response Form -->
        <form @submit.prevent="submitRsvp" class="space-y-6">
          <fieldset class="space-y-3">
            <legend class="text-lg font-semibold text-gray-700 mb-3">
              Will you be able to attend the wedding?
            </legend>

            <label
              class="flex items-center p-3 border rounded-lg cursor-pointer transition duration-150"
              :class="
                familyResponse === 'Attending'
                  ? 'border-green-500 bg-green-50 shadow-md'
                  : 'border-gray-300 hover:border-green-400'
              "
            >
              <input
                type="radio"
                v-model="familyResponse"
                value="Attending"
                class="form-radio text-green-600 focus:ring-green-500"
                required
              />
              <span class="ml-3 font-medium text-gray-700 flex items-center">
                <UserCheck class="w-5 h-5 mr-2 text-green-600" /> Yes, We will be celebrating!
              </span>
            </label>

            <label
              class="flex items-center p-3 border rounded-lg cursor-pointer transition duration-150"
              :class="
                familyResponse === 'Declined'
                  ? 'border-red-500 bg-red-50 shadow-md'
                  : 'border-gray-300 hover:border-red-400'
              "
            >
              <input
                type="radio"
                v-model="familyResponse"
                value="Declined"
                class="form-radio text-red-600 focus:ring-red-500"
                required
              />
              <span class="ml-3 font-medium text-gray-700 flex items-center">
                <X class="w-5 h-5 mr-2 text-red-600" /> No, We unfortunately cannot make it.
              </span>
            </label>
          </fieldset>

          <!-- Attending Count Selector -->
          <div
            v-if="familyResponse === 'Attending'"
            class="p-4 bg-gray-50 rounded-lg border border-gray-200"
          >
            <label for="attending-count" class="block text-lg font-semibold text-gray-700 mb-2">
              How many people in your party will be attending?
            </label>
            <select
              id="attending-count"
              v-model.number="attendingCount"
              class="w-full p-3 border border-gray-300 rounded-lg focus:border-pink-500 focus:ring-1 focus:ring-pink-500 transition duration-150"
              required
            >
              <option v-for="n in Number(maxFamilyGuests)" :key="n" :value="n">
                {{ n }} Guest{{ n !== 1 ? 's' : '' }}
              </option>
            </select>
            <p class="text-sm text-gray-500 mt-2">
              Maximum capacity for your party is {{ maxFamilyGuests }} guest{{
                maxFamilyGuests > 1 ? 's' : ''
              }}.
            </p>
          </div>

          <button
            type="submit"
            class="w-full px-6 py-4 text-xl font-bold text-white bg-pink-600 rounded-lg shadow-lg hover:bg-pink-700 transition duration-300 transform hover:scale-[1.01] flex items-center justify-center"
            :disabled="isLoading"
          >
            <Loader2 v-if="isLoading" class="w-5 h-5 mr-2 animate-spin" />
            <span v-else>Confirm RSVP for {{ selectedHeadGuest.name }} and Family</span>
          </button>

          <button
            @click="((selectedHeadGuest = null), (isRsvpSubmitted = false))"
            type="button"
            class="w-full text-sm text-gray-500 hover:text-pink-600 mt-4 transition duration-150"
          >
            Not me? Change Search
          </button>
        </form>
      </section>
    </div>

    <div class="flex items-center justify-center max-w-3xl mx-auto mt-4 p-4 text-gray-400">
      <a href="/" class="font-bold no-underline hover:text-gray-600 transition-colors"> Home </a>
    </div>
  </div>
</template>
