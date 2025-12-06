<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { Mail, Gift, Hotel } from 'lucide-vue-next'
import weddingHero from '@/images/blue_flower.webp'

// Reactive State
const opacity = ref(1)
// DOM Reference: Must be ref(null)
const heroRef = ref(null)

// Static Data
const weddingData = {
  coupleNames: 'Nour-Eldeen & Tesneem',
  date: 'Saturday, April 11, 2026',
  announcement:
    'We are thrilled to invite you to celebrate our marriage at the Islamic Center of Chester County.',
  address: '1001 Pottstown Pike, West Chester, PA 19380',
  rsvpDeadline: 'January 30th, 2026',
  gifts: {
    message:
      'Your presence is the greatest gift of all. However, if you wish to honor us with a gift, we prefer envelope gifts, or click the link below.',
    links: [{ name: 'Venmo', link: 'https://account.venmo.com/u/neemster' }],
  },
  hotels: {
    message: "We've reserved blocks of rooms at a few nearby hotels for your convenience.",
    options: [
      {
        name: 'Hotel Indigo West Chester',
        link: 'https://www.ihg.com/hotels/us/en/find-hotels/select-roomrate?fromRedirect=true&qSrt=sAV&qIta=99618783&icdv=99618783&glat=META&qSlH=PHLWE&qRms=1&qAdlt=2&qChld=0&qCiD=11&qCiMy=032026&qCoD=12&qCoMy=032026&qrtPt=287.00&setPMCookies=true&qSlRc=KIEN&qRtP=IDAPF&qSHBrC=IN&qDest=39%20E.%20Gay%20Street,%20West%20Chester,%20PA,%20US&partnerVerification=false&channel=GHPA&userSelectedRatePlan=KIENIDAPF&userBookingWindow=126&hmGUID=0a183bac-e5c8-4ad5-9b57-dd9e8918d97f&clk_src=bl&isHotelCampaign=true&partnerRateShown=287.00&gbraid=0AAAAAD4keY88ADSUlHqI98N34aKkatdgh&partnerDateType=selected&mktgvar=hpa_paid_US_desktop_PHLWE_mapresults_1_USD_2026-04-11_selected_22712888848__FALSE_KIENIDAPF&userCountryCode=US&partnerTotalRateShown=318.57&userDeviceType=desktop&adjustMonth=true&partnerClickType=hotel&partnerCurrencyCode=USD&partnerAdSite=mapresults&cm_mmc=hpa_paid_META_IN_PHLWE_desktop&partnerAdType=paid&srb_u=1&qRmFltr=',
        rate: '$273/night',
      },
      {
        name: 'Hotel Warner',
        link: 'https://www.hotelwarner.com/engine/bookingstep1.html?idtokenprovider=100380153&checkin=11%2F04%2F2026&nights=1&lang=en&hsri=02040&adults=2&children=0&ages=0&babies=0&currency=USD&rates=NjQ0MDB8ODEyMzB8NDMyODYzYjB8NDk0Mzl8NDM4MjIz&tracking=&UserDevice=desktop&clickorigin=NOT-RBM&date_type=selected&campaign_id=organic&googlesite=mapresults&tt_meta=gha&PPA1=FALSE&user_list_id=&clk_src=&prid=&step=1&home=https%3A%2F%2Fwww.hotelwarner.com%2F&parties=WyB7CiAgImFkdWx0cyIgOiAyLAogICJjaGlsZHJlbiIgOiBbIF0KfSBd#url=true',
        rate: '$213/night',
      },
    ],
  },
}

// Function to handle the scroll effect
const handleScroll = () => {
  // CRITICAL: Access reactive references with .value in script logic
  if (heroRef.value) {
    const scrollPosition = window.scrollY
    const fadeDistance = 300

    let newOpacity = 1 - (scrollPosition / fadeDistance) * 0.8
    newOpacity = Math.max(0.2, Math.min(1, newOpacity))

    opacity.value = newOpacity
  }
}

// Lifecycle Hooks
onMounted(() => {
  window.addEventListener('scroll', handleScroll)
  handleScroll()
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<template>
  <div class="min-h-screen bg-gray-50 font-sans text-gray-700">
    <!-- Navigation Bar -->
    <nav class="sticky top-0 z-50 bg-white/90 backdrop-blur-sm shadow-md">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex justify-center space-x-6">
        <a
          href="#rsvp"
          class="text-gray-700 hover:text-pink-600 font-medium transition duration-150"
          >RSVP</a
        >
        <a
          href="#gifts"
          class="text-gray-700 hover:text-pink-600 font-medium transition duration-150"
          >Gifts</a
        >
        <a
          href="#hotels"
          class="text-gray-700 hover:text-pink-600 font-medium transition duration-150"
          >Hotels</a
        >
      </div>
    </nav>

    <!-- 1. Announcement Section (Hero with Scroll Fade) -->
    <div
      ref="heroRef"
      class="h-[80vh] min-h-[500px] flex items-center justify-center relative bg-gray-900 overflow-hidden"
    >
      <!-- Background Image with Dynamic Opacity -->
      <div
        class="absolute inset-0 bg-cover bg-center transition-opacity duration-100"
        :style="{
          backgroundImage: `url(${weddingHero})`,
          backgroundAttachment: 'fixed',
          opacity: opacity,
        }"
        aria-label="Background image of the couple"
      ></div>

      <!-- Darker Overlay for Text Contrast -->
      <div class="absolute inset-0 bg-gray-900/0"></div>

      <!-- Announcement Content -->
      <div
        class="relative text-center p-6 bg-white/60 backdrop-blur-md rounded-xl shadow-2xl max-w-lg mx-4 border-2 border-white/50"
      >
        <h1 class="text-6xl sm:text-7xl font-serif text-gray-800 tracking-tight mb-2">
          {{ weddingData.coupleNames }}
        </h1>
        <h2 class="text-lg sm:text-xl font-semibold text-pink-600 mb-4">Are Getting Married!</h2>
        <p class="text-base sm:text-lg text-gray-700 font-medium italic">
          {{ weddingData.announcement }}
        </p>
        <p class="text-base sm:text-lg text-gray-700 font-medium italic">
          {{ weddingData.address }}
        </p>
        <p class="mt-4 text-2xl font-bold text-gray-900">
          {{ weddingData.date }}
        </p>
      </div>
    </div>

    <main class="pb-16">
      <!-- 2. RSVP Section -->
      <section id="rsvp" class="py-16 sm:py-24 bg-white border-b border-gray-100">
        <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div class="text-gray-500 mb-4 flex justify-center">
            <Mail :size="40" class="text-pink-600" />
          </div>
          <h2
            class="text-4xl font-serif text-gray-800 mb-12 border-b-2 border-pink-100 inline-block pb-1"
          >
            Kindly RSVP
          </h2>

          <p class="text-xl mb-8 leading-relaxed">
            Please let us know if you can make it by our deadline:
          </p>
          <p class="text-2xl font-semibold text-gray-900 mb-8">
            {{ weddingData.rsvpDeadline }}
          </p>

          <a
            href="/rsvp"
            class="inline-block px-10 py-4 text-xl font-bold text-white bg-pink-600 rounded-full shadow-lg hover:bg-pink-700 transition duration-300 transform hover:scale-105"
            aria-label="Link to RSVP form"
          >
            Submit Your RSVP
          </a>
        </div>
      </section>

      <!-- 3. Gifts Section -->
      <section id="gifts" class="py-16 sm:py-24 bg-white border-b border-gray-100">
        <div class="max-w-4xl mx-auto px-2 sm:px-3 lg:px-2 text-center">
          <div class="text-gray-500 mb-4 flex justify-center">
            <Gift :size="40" class="text-pink-600" />
          </div>
          <h2
            class="text-4xl font-serif text-gray-800 mb-12 border-b-2 border-pink-100 inline-block pb-1"
          >
            Gifts
          </h2>

          <p class="text-lg leading-relaxed mb-8 max-w-2xl mx-auto">
            {{ weddingData.gifts.message }}
          </p>
          <div class="flex justify-center flex-wrap gap-6">
            <a
              v-for="(payment, index) in weddingData.gifts.links"
              :key="index"
              :href="payment.link"
              target="_blank"
              rel="noopener noreferrer"
              class="block p-2"
            >
              <span class="text-xl text-gray-800 block">{{ payment.name }}</span>
            </a>
          </div>
        </div>
      </section>

      <!-- 4. Hotels Section -->
      <section id="hotels" class="py-16 sm:py-24 bg-white border-b border-gray-100">
        <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div class="text-gray-500 mb-4 flex justify-center">
            <Hotel :size="40" class="text-pink-600" />
          </div>
          <h2
            class="text-4xl font-serif text-gray-800 mb-12 border-b-2 border-pink-100 inline-block pb-1"
          >
            Area Accommodations
          </h2>

          <p class="text-lg leading-relaxed mb-8 max-w-2xl mx-auto">
            {{ weddingData.hotels.message }}
          </p>
          <div class="flex justify-center flex-wrap gap-8">
            <div
              v-for="(option, index) in weddingData.hotels.options"
              :key="index"
              class="w-full sm:w-80 p-6 bg-white rounded-xl shadow-lg border border-gray-200 text-left"
            >
              <h3 class="text-2xl font-bold text-gray-900 mb-2">{{ option.name }}</h3>
              <p class="text-md text-gray-600 mb-4">
                <span class="font-semibold text-pink-600">{{ option.rate }}</span>
              </p>
              <a
                :href="option.link"
                target="_blank"
                rel="noopener noreferrer"
                class="text-sm font-semibold text-pink-600 hover:text-pink-700 underline"
              >
                Book Your Room &rarr;
              </a>
            </div>
          </div>
        </div>
      </section>
    </main>

    <footer class="py-8 text-center text-gray-500 text-sm bg-gray-100">
      &copy; 2026 {{ weddingData.coupleNames }}. We can't wait to celebrate with you!
    </footer>
  </div>
</template>
